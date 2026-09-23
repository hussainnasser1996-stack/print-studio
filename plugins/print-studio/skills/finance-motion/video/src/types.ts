export type Theme = {ink: string; paper: string; panel: string; accent: string; gold: string; pos: string; neg: string; muted: string};
export type Kpi = {id: string; label: string; value: number; display: string; delta: string; direction: "up" | "down"; good: boolean};
export type Point = {label: string; value: number; display: string};
export type Segment = {label: string; color?: string; revenue: number; revenue_prior: number; op_profit: number; display: Record<string, string>};
export type Node = {label: string; value: number; display: string};
export type Row = {label: string; values: number[]; display: string[]; total?: boolean};
export type Report = {
  meta: {company: string; fictional?: boolean; period: string; prior_period?: string; units?: string; source: string; theme: Theme};
  kpis: Kpi[];
  revenue_history: {title: string; unit?: string; points: Point[]};
  segments: {title: string; total: Segment; items: Segment[]};
  bridge: {title: string; start: Node; steps: Node[]; end: Node};
  income_statement: {title: string; columns: string[]; rows: Row[]};
};
export type Props = {report: Report; format: "4x5" | "9x16" | "16x9"};
