import {
  createFactoryRuntime,
  dispatchFactoryRuntime,
  tickFactoryRuntime,
  type TamaFactoryRuntime,
} from "./factory-hooks";
import type { TamaRuntimeBootstrapConfigFile } from "./runtime-config";
import type { TamaDispatchAction } from "./dispatcher";
import type { TamaGDevelopExport } from "./gdevelop-state";

export interface TamaFactoryScenarioStep {
  type: "dispatch" | "tick";
  action?: TamaDispatchAction;
  now?: number;
}

export interface TamaFactoryScenarioResult {
  runtime: TamaFactoryRuntime;
  outputs: TamaGDevelopExport[];
}

export function runFactoryScenario(
  config: TamaRuntimeBootstrapConfigFile | undefined,
  steps: TamaFactoryScenarioStep[],
  now = Date.now(),
): TamaFactoryScenarioResult {
  let runtime = createFactoryRuntime(config, now);
  const outputs: TamaGDevelopExport[] = [runtime.bundle.gdevelop];

  for (const step of steps) {
    if (step.type === "tick") {
      const tick = tickFactoryRuntime(runtime, step.now ?? Date.now());
      runtime = tick.runtime;
      outputs.push(tick.gdevelop);
      continue;
    }

    if (step.type === "dispatch" && step.action) {
      const dispatched = dispatchFactoryRuntime(runtime, step.action);
      runtime = dispatched.runtime;
      outputs.push(dispatched.gdevelop);
    }
  }

  return {
    runtime,
    outputs,
  };
}
