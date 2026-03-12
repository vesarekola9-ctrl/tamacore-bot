import {
  createFactoryExportBundle,
  type TamaFactoryExportBundle,
} from "./factory-export";
import {
  createLiveLoop,
  tickLiveLoop,
  type TamaLiveLoopState,
  type TamaLiveLoopTickResult,
} from "./live-loop";
import {
  dispatchSessionAction,
  type TamaDispatchAction,
  type TamaDispatchResponse,
} from "./dispatcher";
import {
  exportSnapshotToGDevelop,
  type TamaGDevelopExport,
} from "./gdevelop-state";
import {
  createBridgeSnapshot,
  type TamaBridgeSnapshot,
} from "./bridge";
import type { TamaRuntimeBootstrapConfigFile } from "./runtime-config";
import type { TamaSessionState } from "./session";

export interface TamaFactoryRuntime {
  loop: TamaLiveLoopState;
  bundle: TamaFactoryExportBundle;
}

export interface TamaFactoryDispatchResult {
  runtime: TamaFactoryRuntime;
  response: TamaDispatchResponse;
  snapshot: TamaBridgeSnapshot;
  gdevelop: TamaGDevelopExport;
}

export interface TamaFactoryTickResult {
  runtime: TamaFactoryRuntime;
  tick: TamaLiveLoopTickResult;
  gdevelop: TamaGDevelopExport;
}

function cloneRuntimeConfig(
  input?: TamaRuntimeBootstrapConfigFile,
): TamaRuntimeBootstrapConfigFile | undefined {
  if (!input) return undefined;

  return {
    pet: input.pet
      ? {
          ...input.pet,
          activeEffects: Array.isArray(input.pet.activeEffects)
            ? [...input.pet.activeEffects]
            : [],
        }
      : undefined,
    inventory: Array.isArray(input.inventory)
      ? input.inventory.map((entry) => ({ ...entry }))
      : [],
    items: Array.isArray(input.items)
      ? input.items.map((item) => ({
          ...item,
          changes: Array.isArray(item.changes)
            ? item.changes.map((change) => ({ ...change }))
            : [],
          timedEffects: Array.isArray(item.timedEffects)
            ? item.timedEffects.map((effect) => ({ ...effect }))
            : [],
          tags: Array.isArray(item.tags) ? [...item.tags] : [],
        }))
      : [],
    quests: Array.isArray(input.quests)
      ? input.quests.map((quest) => ({
          ...quest,
          objectives: Array.isArray(quest.objectives)
            ? quest.objectives.map((objective) => ({ ...objective }))
            : [],
          rewards: Array.isArray(quest.rewards)
            ? quest.rewards.map((reward) => ({ ...reward }))
            : [],
        }))
      : [],
    coins: input.coins,
    decay: input.decay ? { ...input.decay } : undefined,
    loop: input.loop ? { ...input.loop } : undefined,
  };
}

function replaceRuntimeSession(
  runtime: TamaFactoryRuntime,
  session: TamaSessionState,
): TamaFactoryRuntime {
  return {
    ...runtime,
    loop: {
      ...runtime.loop,
      session,
    },
  };
}

export function createFactoryRuntime(
  input?: TamaRuntimeBootstrapConfigFile,
  now = Date.now(),
): TamaFactoryRuntime {
  const cloned = cloneRuntimeConfig(input);

  return {
    loop: createLiveLoop({
      pet: cloned?.pet,
      inventory: cloned?.inventory,
      items: cloned?.items,
      quests: cloned?.quests,
      coins: cloned?.coins,
      decay: cloned?.decay,
      loop: cloned?.loop,
      now,
    }),
    bundle: createFactoryExportBundle(cloned, now),
  };
}

export function tickFactoryRuntime(
  runtime: TamaFactoryRuntime,
  now = Date.now(),
): TamaFactoryTickResult {
  const tick = tickLiveLoop(runtime.loop, now);
  const nextRuntime: TamaFactoryRuntime = {
    ...runtime,
    loop: tick.state,
  };

  return {
    runtime: nextRuntime,
    tick,
    gdevelop: exportSnapshotToGDevelop(tick.snapshot),
  };
}

export function dispatchFactoryRuntime(
  runtime: TamaFactoryRuntime,
  action: TamaDispatchAction,
): TamaFactoryDispatchResult {
  const response = dispatchSessionAction(
    { session: runtime.loop.session },
    action,
  );

  if (!response.ok || !response.session) {
    const snapshot = createBridgeSnapshot(runtime.loop.session);
    return {
      runtime,
      response,
      snapshot,
      gdevelop: exportSnapshotToGDevelop(snapshot),
    };
  }

  const nextRuntime = replaceRuntimeSession(runtime, response.session);
  const snapshot = createBridgeSnapshot(response.session);

  return {
    runtime: nextRuntime,
    response,
    snapshot,
    gdevelop: exportSnapshotToGDevelop(snapshot),
  };
}
