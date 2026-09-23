#!/usr/bin/env python3
"""Validate a finance-motion report.json BEFORE anything is rendered.

Every output (PDF, MP4, HTML) is drawn from this one file, so a wrong number here is wrong
everywhere at once. This script refuses to pass a file whose numbers don't foot:

  1. display == value      every "display" string parses back to its numeric "value"
                           ("(2,612)" == -2612, "$4.82B" == 4.82, "27.2%" == 27.2)
  2. totals foot           segment revenue / prior / op profit sum to the group total;
                           income-statement totals equal the rows in "sum_of"
  3. bridge closes         start + steps == end, and each step == that segment's change
  4. ratios recompute      segment growth, margin and share, and the KPI deltas, recompute
                           from the underlying values to the precision they are displayed at
  5. KPIs tie              headline KPIs agree with the tables they summarise

Usage:  python validate_report.py report.json      (exit 1 on any failure)
        python validate_report.py --selftest       (corrupts a copy; every check must fire)
"""
import copy, json, re, sys
from decimal import Decimal, ROUND_HALF_UP

fails = []


def fail(msg):
    fails.append(msg)


def parse(display):
    """'(2,612)' -> -2612.0 ; '$4.82B' -> 4.82 ; '−0.06x' -> -0.06 ; '+110 bps' -> 110.0"""
    s = str(display).replace("−", "-").replace(",", "")
    neg = s.strip().startswith("(") and s.strip().endswith(")")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    v = float(m.group())
    return -abs(v) if neg else v


def decimals(display):
    m = re.search(r"\d+(?:\.(\d+))?", str(display).replace(",", ""))
    return len(m.group(1)) if m and m.group(1) else 0


def rounds_to(x, display):
    """Does x, rounded half-up to the display's precision, equal the displayed number?"""
    d = decimals(display)
    q = Decimal(1).scaleb(-d)
    return Decimal(str(x)).quantize(q, ROUND_HALF_UP) == Decimal(str(abs(parse(display)))).quantize(q)


def pct(a, b):
    return (a / b - 1) * 100


def check_display(path, value, display):
    p = parse(display)
    if p is None or abs(p - value) > 1e-9 * max(1, abs(value)):
        fail(f"{path}: display {display!r} does not match value {value}")


def validate(r):
    fails.clear()
    # 1. display == value, everywhere a pair exists
    for k in r.get("kpis", []):
        check_display(f"kpis.{k['id']}", k["value"], k["display"])
    for p in r.get("revenue_history", {}).get("points", []):
        check_display(f"revenue_history.{p['label']}", p["value"], p["display"])
    seg = r.get("segments")
    if seg:
        for it in seg["items"] + [seg["total"]]:
            for f in ("revenue", "revenue_prior", "op_profit"):
                check_display(f"segments.{it['label']}.{f}", it[f], it["display"][f])
    br = r.get("bridge")
    if br:
        for node in [br["start"], *br["steps"], br["end"]]:
            check_display(f"bridge.{node['label']}", node["value"], node["display"])
    inc = r.get("income_statement")
    if inc:
        for row in inc["rows"]:
            for v, d in zip(row["values"], row["display"]):
                check_display(f"income_statement.{row['label']}", v, d)

    # 2. totals foot
    if seg:
        tot = seg["total"]
        for f in ("revenue", "revenue_prior", "op_profit"):
            s = sum(it[f] for it in seg["items"])
            if s != tot[f]:
                fail(f"segments: {f} items sum to {s}, total says {tot[f]}")
    if inc:
        by = {row["label"]: row for row in inc["rows"]}
        for row in inc["rows"]:
            for i, col in enumerate(inc["columns"]):
                if "sum_of" in row:
                    s = sum(by[l]["values"][i] for l in row["sum_of"])
                    if s != row["values"][i]:
                        fail(f"income_statement.{row['label']} {col}: rows sum to {s}, total says {row['values'][i]}")

    # 3. bridge closes, and each step equals the segment's change
    if br:
        s = br["start"]["value"] + sum(st["value"] for st in br["steps"])
        if s != br["end"]["value"]:
            fail(f"bridge: start + steps = {s}, end says {br['end']['value']}")
        if seg:
            items = {it["label"]: it for it in seg["items"]}
            for st in br["steps"]:
                it = items.get(st["label"])
                if it and it["revenue"] - it["revenue_prior"] != st["value"]:
                    fail(f"bridge.{st['label']}: step {st['value']} != segment change {it['revenue'] - it['revenue_prior']}")
            if br["start"]["value"] != seg["total"]["revenue_prior"] or br["end"]["value"] != seg["total"]["revenue"]:
                fail("bridge: start/end do not match the segment totals")

    # 4. ratios recompute at displayed precision
    if seg:
        tot = seg["total"]
        for it in seg["items"] + [tot]:
            d, name = it["display"], it["label"]
            if "growth" in d and not rounds_to(pct(it["revenue"], it["revenue_prior"]), d["growth"]):
                fail(f"segments.{name}.growth: {d['growth']} but recomputes to {pct(it['revenue'], it['revenue_prior']):.3f}%")
            if "margin" in d and not rounds_to(it["op_profit"] / it["revenue"] * 100, d["margin"]):
                fail(f"segments.{name}.margin: {d['margin']} but recomputes to {it['op_profit'] / it['revenue'] * 100:.3f}%")
            if "share" in d and not rounds_to(it["revenue"] / tot["revenue"] * 100, d["share"]):
                fail(f"segments.{name}.share: {d['share']} but recomputes to {it['revenue'] / tot['revenue'] * 100:.3f}%")

    # 5. KPIs tie to the tables (only the ids this schema defines; others are free-form)
    k = {x["id"]: x for x in r.get("kpis", [])}
    if seg and inc:
        tot = seg["total"]
        by = {row["label"]: row for row in inc["rows"]}
        ties = []
        if "revenue" in k:
            ties.append(("revenue", tot["revenue"] / 1000, by.get("Revenue", {}).get("values", [None, None])))
        if "op_profit" in k:
            ties.append(("op_profit", tot["op_profit"] / 1000, by.get("Operating profit", {}).get("values", [None, None])))
        for kid, scaled, row in ties:
            if not rounds_to(scaled, k[kid]["display"]):
                fail(f"kpis.{kid}: {k[kid]['display']} vs segment total {scaled}")
            if row[0] is not None and row[1]:
                if not rounds_to(pct(row[0], row[1]), k[kid]["delta"]):
                    fail(f"kpis.{kid}.delta: {k[kid]['delta']} but recomputes to {pct(row[0], row[1]):+.3f}%")
        if "op_margin" in k and not rounds_to(tot["op_profit"] / tot["revenue"] * 100, k["op_margin"]["display"]):
            fail(f"kpis.op_margin: {k['op_margin']['display']} vs {tot['op_profit'] / tot['revenue'] * 100:.3f}%")
    for kid, x in k.items():
        sign = parse(x.get("delta", "0"))
        if sign is not None and sign != 0 and (sign > 0) != (x.get("direction") == "up"):
            fail(f"kpis.{kid}: delta {x['delta']} disagrees with direction {x.get('direction')!r}")
    hist = r.get("revenue_history", {}).get("points", [])
    if hist and seg:
        if not rounds_to(seg["total"]["revenue"] / 1000, hist[-1]["display"]):
            fail(f"revenue_history.{hist[-1]['label']}: {hist[-1]['display']} vs segment total {seg['total']['revenue'] / 1000}")
        if len(hist) > 1 and not rounds_to(seg["total"]["revenue_prior"] / 1000, hist[-2]["display"]):
            fail(f"revenue_history.{hist[-2]['label']}: {hist[-2]['display']} vs prior total {seg['total']['revenue_prior'] / 1000}")
    return list(fails)


def selftest(path):
    base = json.load(open(path))
    assert not validate(base), f"the sample itself fails: {fails}"
    cases = {
        "display != value":   lambda r: r["income_statement"]["rows"][1].__setitem__("display", ["(2,621)", "(2,431)"]),
        "segment sum":        lambda r: (r["segments"]["items"][0].__setitem__("op_profit", 821),
                                         r["segments"]["items"][0]["display"].__setitem__("op_profit", "821")),
        "bridge closes":      lambda r: r["bridge"]["steps"][3].update(value=13, display="+13"),
        "growth recompute":   lambda r: r["segments"]["items"][1]["display"].__setitem__("growth", "20.4%"),
        "kpi delta":          lambda r: r["kpis"][1].__setitem__("delta", "+16.2%"),
        "direction sign":     lambda r: r["kpis"][5].__setitem__("delta", "+0.06x"),
        "income total":       lambda r: (r["income_statement"]["rows"][7].__setitem__("values", [936, 790]),
                                         r["income_statement"]["rows"][7].__setitem__("display", ["936", "790"])),
    }
    ok = True
    for name, corrupt in cases.items():
        r = copy.deepcopy(base)
        corrupt(r)
        got = validate(r)
        print(f"  {'caught' if got else 'MISSED'}  {name}" + (f"  -> {got[0]}" if got else ""))
        ok &= bool(got)
    print("SELFTEST", "PASSED: every planted error was caught" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        import pathlib
        sample = pathlib.Path(__file__).resolve().parent.parent / "examples/meridian/report.json"
        sys.exit(0 if selftest(sys.argv[2] if len(sys.argv) > 2 else sample) else 1)
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    errs = validate(json.load(open(sys.argv[1])))
    for e in errs:
        print("FAIL", e)
    print("RESULT:", "FAIL" if errs else "PASS — every total foots, every ratio recomputes")
    sys.exit(1 if errs else 0)
