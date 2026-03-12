import {
  createFullLoop,
  tickFullLoop,
  dispatchFullLoopAction,
  type TamaFullLoopActionResult,
  type TamaFullLoopState,
  type TamaFullLoopTickResult,
} from "./full-loop-controller";
import {
  createAiControllerState,
  runAiStep,
  type TamaAiControllerState,
  type TamaAiStepResult,
} from "./ai-bot-controller";
import { createUiBridgeSnapshot, type TamaUiBridgeSnapshot } from "./ui-bridge";
import type { TamaAnyLiveLoopAction } from "./gdevelop-live-loop";

export interface TamaRuntimeInstance {
  loop: TamaFullLoopState;
  ai: TamaAiControllerState;
  running: boolean;
  autoAi: boolean;
  startedAt: number;
  lastUpdate: number;
  tickCount: number;
}

export interface TamaRuntimeStepResult {
  runtime: TamaRuntimeInstance;
  tick: TamaFullLoopTickResult;
  ai?: TamaAiStepResult;
}

export interface TamaRuntimeActionResult {
  runtime: TamaRuntimeInstance;
  result: TamaFullLoopActionResult;
}

function cloneRuntime(runtime: TamaRuntimeInstance): TamaRuntimeInstance {
  return {
    loop: runtime.loop,
    ai: {
      config: { ...runtime.ai.config },
      lastDecisionAt: runtime.ai.lastDecisionAt,
      decisionCount: runtime.ai.decisionCount,
    },
    running: runtime.running,
    autoAi: runtime.autoAi,
    startedAt: runtime.startedAt,
    lastUpdate: runtime.lastUpdate,
    tickCount: runtime.tickCount,
  };
}

export function createRuntime(): TamaRuntimeInstance {
  const now = Date.now();

  return {
    loop: createFullLoop(),
    ai: createAiControllerState(),
    running: false,
    autoAi: true,
    startedAt: now,
    lastUpdate: now,
    tickCount: 0,
  };
}

export function startRuntime(runtime: TamaRuntimeInstance): TamaRuntimeInstance {
  const next = cloneRuntime(runtime);
  next.running = true;
  next.lastUpdate = Date.now();
  return next;
}

export function stopRuntime(runtime: TamaRuntimeInstance): TamaRuntimeInstance {
  const next = cloneRuntime(runtime);
  next.running = false;
  next.lastUpdate = Date.now();
  return next;
}

export function setRuntimeAiEnabled(
  runtime: TamaRuntimeInstance,
  enabled: boolean,
): TamaRuntimeInstance {
  const next = cloneRuntime(runtime);
  next.autoAi = enabled;
  next.lastUpdate = Date.now();
  return next;
}

export function dispatchRuntimeAction(
  runtime: TamaRuntimeInstance,
  action: TamaAnyLiveLoopAction,
): TamaRuntimeActionResult {
  const result = dispatchFullLoopAction(runtime.loop, action);

  const next = cloneRuntime(runtime);
  next.loop = result.state;
  next.lastUpdate = Date.now();

  return {
    runtime: next,
    result,
  };
}

export function stepRuntime(
  runtime: TamaRuntimeInstance,
  now = Date.now(),
): TamaRuntimeStepResult {
  if (!runtime.running) {
    const idleTick: TamaFullLoopTickResult = {
      state: runtime.loop,
      tick: {
        state: runtime.loop.liveLoop,
        snapshot: runtime.loop.ui.gdevelop
          ? (undefined as never)
          : (undefined as never),
        consumedEventCount: 0,
        claimedQuestIds: [],
      },
    };

    return {
      runtime,
      tick: idleTick,
    };
  }

  const tick = tickFullLoop(runtime.loop, now);

  const next = cloneRuntime(runtime);
  next.loop = tick.state;
  next.lastUpdate = now;
  next.tickCount += 1;

  if (!next.autoAi) {
    return {
      runtime: next,
      tick,
    };
  }

  const ai = runAiStep(next.loop, next.ai, now);
  next.loop = ai.loop;
  next.ai = ai.ai;
  next.lastUpdate = now;

  return {
    runtime: next,
    tick,
    ai,
  };
}

export function getRuntimeLoop(
  runtime: TamaRuntimeInstance,
): TamaFullLoopState {
  return runtime.loop;
}

export function getRuntimeUi(
  runtime: TamaRuntimeInstance,
): TamaUiBridgeSnapshot {
  return createUiBridgeSnapshot(runtime.loop.liveLoop);
}

export function isRuntimeRunning(runtime: TamaRuntimeInstance): boolean {
  return runtime.running;
}
