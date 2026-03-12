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
import { pruneNotifications, pruneSessionEvents } from "./pruning";
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

function enforceRuntimeLimits(runtime: TamaFactoryRuntime, now: number): TamaFactoryRuntime {
  const session: TamaSessionState = {
    ...runtime.loop.session,
    notifications: runtime.loop.session.notifications.map((entry) => ({ ...entry })),
    events: runtime.loop.session.events.map((entry) => ({
      ...entry,
      payload:
        entry.payload && typeof entry.payload === "object"
          ? { ...(entry.payload as Record<string, unknown>) }
          : entry.payload,
    })),
  };

  pruneNotifications(session, runtime.loop.config.loop.notificationLimit, now);
  pruneSessionEvents(session, runtime.loop.config.loop.eventQueueLimit, now);

  return {
    ...runtime,
    loop: {
      ...runtime.loop,
      session,
      updatedAt: now,
    },
  };
}

function replaceRuntimeSession(
  runtime: TamaFactoryRuntime,
  session: TamaSessionState,
  now: number,
): TamaFactoryRuntime {
  return enforceRuntimeLimits(
    {
      ...runtime,
      loop: {
        ...runtime.loop,
        session,
        updatedAt: now,
      },
    },
    now,
  );
}

export function createFactoryRuntime(
  input?: TamaRuntimeBootstrapConfigFile,
  now = Date.now(),
): TamaFactoryRuntime {
  const cloned = cloneRuntimeConfig(input);

  return enforceRuntimeLimits(
    {
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
    },
    now,
  );
}

export function tickFactoryRuntime(
  runtime: TamaFactoryRuntime,
  now = Date.now(),
): TamaFactoryTickResult {
  const tick = tickLiveLoop(runtime.loop, now);
  const nextRuntime = enforceRuntimeLimits(
    {
      ...runtime,
      loop: tick.state,
    },
    now,
  );

  return {
    runtime: nextRuntime,
    tick: {
      ...tick,
      state: nextRuntime.loop,
      snapshot: createBridgeSnapshot(nextRuntime.loop.session),
    },
    gdevelop: exportSnapshotToGDevelop(createBridgeSnapshot(nextRuntime.loop.session)),
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

  const now =
    "payload" in action && action.payload && typeof action.payload === "object" && "now" in action.payload
      ? (action.payload as { now?: number }).now ?? Date.now()
      : Date.now();

  const nextRuntime = replaceRuntimeSession(runtime, response.session, now);
  const snapshot = createBridgeSnapshot(nextRuntime.loop.session);

  return {
    runtime: nextRuntime,
    response: {
      ...response,
      session: nextRuntime.loop.session,
      snapshot,
    },
    snapshot,
    gdevelop: exportSnapshotToGDevelop(snapshot),
  };
}
