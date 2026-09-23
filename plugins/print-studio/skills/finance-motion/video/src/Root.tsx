import React from "react";
import {Composition} from "remotion";
import {FinanceReel, TOTAL} from "./Reel";
import {Props} from "./types";
import timing from "./timing.json";
import sample from "../../examples/meridian/report.json";

export const Root: React.FC = () => (
  <Composition
    id="FinanceReel"
    component={FinanceReel}
    fps={timing.fps}
    durationInFrames={TOTAL}
    width={1080}
    height={1350}
    defaultProps={{report: sample, format: "4x5"} as Props}
    calculateMetadata={({props}) => {
      const fmt = timing.formats[(props.format || "4x5") as keyof typeof timing.formats];
      return {width: fmt.width, height: fmt.height};
    }}
  />
);
