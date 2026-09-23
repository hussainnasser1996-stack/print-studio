import React from "react";
import {Sequence} from "remotion";
import {Props} from "./types";
import timing from "./timing.json";
import {Stage, SceneFade} from "./ui";
import {Title, Kpis, RevenueHistory, Segments, Bridge, IncomeStatement, End} from "./scenes";

export const TOTAL = timing.scenes.reduce((s, x) => s + x.frames, 0);

export const FinanceReel: React.FC<Props> = ({report}) => {
  let from = 0;
  const holdOf = (id: string) => timing.scenes.find((s) => s.id === id)?.hold_from ?? 0;
  const body: Record<string, React.ReactNode> = {
    title: <Title r={report} />,
    kpis: <Kpis r={report} holdFrom={holdOf("kpis")} />,
    revenue_history: <RevenueHistory r={report} />,
    segments: <Segments r={report} />,
    bridge: <Bridge r={report} />,
    income_statement: <IncomeStatement r={report} />,
    end: <End r={report} />,
  };
  return (
    <Stage theme={report.meta.theme}>
      {timing.scenes.map((s) => {
        const el = (
          <Sequence key={s.id} from={from} durationInFrames={s.frames} name={s.id}>
            <SceneFade frames={s.frames} fade={timing.fade}>{body[s.id]}</SceneFade>
          </Sequence>
        );
        from += s.frames;
        return el;
      })}
    </Stage>
  );
};
