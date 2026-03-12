import {
  dispatchSessionAction,
  type TamaDispatchAction,
  type TamaDispatchResponse,
} from "./dispatcher";
import {
  exportLiveLoopStateToGDevelop,
  type TamaGDevelopExport,
} from "./gdevelop-state";
import {
  createLiveLoop,
  tickLiveLoop,
  type TamaLiveLoopState,
  type TamaLiveLoopTickResult,
} from "./live-loop";
import {
  cloneWorldState,
  setWeather,
  setZone,
  type TamaWorldBootstrapInput,
} from "./world";
import type { TamaBridgeBootstrapInput } from "./bridge";
import type { TamaRuntimeBootstrapConfigFile } from "./runtime-config";

export type TamaLiveLoopActionType =
  | "LIVE_BOOTSTRAP"
  | "LIVE_TICK"
  | "LIVE_SNAPSHOT"
  | "WORLD_SET_ZONE"
  | "WORLD_SET_WEATHER"
  | "BOOTSTRAP"
  | "TICK"
  | "GRANT_COINS"
  | "GRANT_ITEM"
  | "BUY_ITEM"
  | "USE_ITEM"
  | "READ_NOTIFICATION"
  | "READ_ALL_NOTIFICATIONS"
  | "CLEAR_READ_NOTIFICATIONS"
  | "CLAIM_QUEST"
  | "CONSUME_EVENTS"
  | "CLEAR_EVENTS"
  | "SNAPSHOT";

export interface TamaLiveLoopBootstrapAction {
  type: "LIVE_BOOTSTRAP";
  payload?: TamaBridgeBootstrapInput &
    TamaRuntimeBootstrapConfigFile & {
      world?: TamaWorldBootstrapInput;
    };
}

export interface TamaLiveLoopTickAction {
  type: "LIVE_TICK";
  payload?: {
    now?: number;
  };
}

export interface TamaLiveLoopSnapshotAction {
  type: "LIVE_SNAPSHOT";
}

export interface TamaWorldSetZoneAction {
  type: "WORLD_SET_ZONE";
  payload: {
    zone: string;
  };
}

export interface TamaWorldSetWeatherAction {
  type: "WORLD_SET_WEATHER";
  payload: {
    weather: string;
  };
}

export type TamaAnyLiveLoopAction =
  | TamaLiveLoopBootstrapAction
  | TamaLiveLoopTickAction
  | TamaLiveLoopSnapshotAction
  | TamaWorldSetZoneAction
  | TamaWorldSetWeatherAction
  | TamaDispatchAction;

export interface TamaLiveLoopDispatchState {
  liveLoop?: TamaLiveLoopState;
}

export interface TamaLiveLoopDispatchSuccess<T = Record<string, never>> {
  ok: true;
  action: TamaLiveLoopActionType;
  liveLoop: TamaLiveLoopState;
  gdevelop: TamaGDevelopExport;
  result: T;
}

export interface TamaLiveLoopDispatchFailure {
  ok: false;
  action: TamaLiveLoopActionType;
  code:
    | "LIVE_LOOP_REQUIRED"
    | "INVALID_ACTION"
    | "INVALID_PAYLOAD"
    | "UNKNOWN_ACTION";
  error: string;
  liveLoop?: TamaLiveLoopState;
  gdevelop?: TamaGDevelopExport;
}

export type TamaLiveLoopDispatchResponse<T = Record<string, never>> =
  | TamaLiveLoopDispatchSuccess<T>
  | TamaLiveLoopDispatchFailure;

function hasLiveLoop(
  state: TamaLiveLoopDispatchState,
): state is { liveLoop: TamaLiveLoopState } {
  return !!state.liveLoop;
}

function fail(
  action: TamaLiveLoopActionType,
  code: TamaLiveLoopDispatchFailure["code"],
  error: string,
  liveLoop?: TamaLiveLoopState,
): TamaLiveLoopDispatchFailure {
  return {
    ok: false,
    action,
    code,
    error,
    liveLoop,
    gdevelop: liveLoop ? exportLiveLoopStateToGDevelop(liveLoop) : undefined,
  };
}

function requireLiveLoop(
  state: TamaLiveLoopDispatchState,
  action: TamaLiveLoopActionType,
): TamaLiveLoopDispatchFailure | null {
  if (!hasLiveLoop(state)) {
    return fail(
      action,
      "LIVE_LOOP_REQUIRED",
      "Live loop has not been initialized.",
    );
  }

  return null;
}

function success<T>(
  action: TamaLiveLoopActionType,
  liveLoop: TamaLiveLoopState,
  result: T,
): TamaLiveLoopDispatchSuccess<T> {
  return {
    ok: true,
    action,
    liveLoop,
    gdevelop: exportLiveLoopStateToGDevelop(liveLoop),
    result,
  };
}

function copyLiveLoopState(input: TamaLiveLoopState): TamaLiveLoopState {
  return {
    ...input,
    session: {
      ...input.session,
      pet: {
        ...input.session.pet,
        activeEffects: Array.isArray(input.session.pet.activeEffects)
          ? input.session.pet.activeEffects.map((effect) => ({ ...effect }))
          : [],
      },
      inventory: input.session.inventory.map((entry) => ({ ...entry })),
      notifications: input.session.notifications.map((entry) => ({ ...entry })),
      quests: input.session.quests.map((entry) => ({
        ...entry,
        objectives: entry.objectives.map((objective) => ({ ...objective })),
        progress: entry.progress.map((progress) => ({ ...progress })),
        rewards: entry.rewards.map((reward) => ({ ...reward })),
      })),
      items: input.session.items.map((entry) => ({
        ...entry,
        changes: Array.isArray(entry.changes)
          ? entry.changes.map((change) => ({ ...change }))
          : [],
        timedEffects: Array.isArray(entry.timedEffects)
          ? entry.timedEffects.map((effect) => ({ ...effect }))
          : [],
        tags: Array.isArray(entry.tags) ? [...entry.tags] : [],
      })),
      events: input.session.events.map((entry) => ({
        ...entry,
        payload:
          entry.payload && typeof entry.payload === "object"
            ? { ...(entry.payload as Record<string, unknown>) }
            : entry.payload,
      })),
    },
    world: cloneWorldState(input.world),
    config: {
      ...input.config,
      pet: { ...input.config.pet },
      inventory: { ...input.config.inventory },
      decay: { ...input.config.decay },
      loop: { ...input.config.loop },
      items: input.config.items.map((item) => ({
        ...item,
        changes: Array.isArray(item.changes)
          ? item.changes.map((change) => ({ ...change }))
          : [],
        timedEffects: Array.isArray(item.timedEffects)
          ? item.timedEffects.map((effect) => ({ ...effect }))
          : [],
        tags: Array.isArray(item.tags) ? [...item.tags] : [],
      })),
      quests: input.config.quests.map((quest) => ({
        ...quest,
        objectives: quest.objectives.map((objective) => ({ ...objective })),
        rewards: quest.rewards.map((reward) => ({ ...reward })),
      })),
    },
  };
}

function mapDispatchErrorCode(
  response: TamaDispatchResponse,
): TamaLiveLoopDispatchFailure["code"] {
  if (response.code === "SESSION_REQUIRED") {
    return "LIVE_LOOP_REQUIRED";
  }

  if (response.code === "INVALID_PAYLOAD") {
    return "INVALID_PAYLOAD";
  }

  if (response.code === "INVALID_ACTION") {
    return "INVALID_ACTION";
  }

  return "UNKNOWN_ACTION";
}

function applySessionDispatchToLiveLoop(
  liveLoop: TamaLiveLoopState,
  response: TamaDispatchResponse,
): TamaLiveLoopDispatchResponse {
  if (!response.ok) {
    return fail(
      response.action as TamaLiveLoopActionType,
      mapDispatchErrorCode(response),
      response.error,
      liveLoop,
    );
  }

  const next = copyLiveLoopState(liveLoop);
  next.session = response.session;
  next.updatedAt = Date.now();

  return success(
    response.action as TamaLiveLoopActionType,
    next,
    response.result,
  );
}

export function dispatchLiveLoopAction(
  state: TamaLiveLoopDispatchState,
  action: TamaAnyLiveLoopAction,
): TamaLiveLoopDispatchResponse {
  switch (action.type) {
    case "LIVE_BOOTSTRAP": {
      const liveLoop = createLiveLoop(action.payload);
      return success("LIVE_BOOTSTRAP", liveLoop, {});
    }

    case "LIVE_TICK": {
      const missing = requireLiveLoop(state, "LIVE_TICK");
      if (missing) return missing;

      const result: TamaLiveLoopTickResult = tickLiveLoop(
        state.liveLoop,
        action.payload?.now ?? Date.now(),
      );

      return success("LIVE_TICK", result.state, {
        consumedEventCount: result.consumedEventCount,
        claimedQuestIds: result.claimedQuestIds,
        snapshot: result.snapshot,
      });
    }

    case "LIVE_SNAPSHOT": {
      const missing = requireLiveLoop(state, "LIVE_SNAPSHOT");
      if (missing) return missing;

      return success("LIVE_SNAPSHOT", state.liveLoop, {});
    }

    case "WORLD_SET_ZONE": {
      const missing = requireLiveLoop(state, "WORLD_SET_ZONE");
      if (missing) return missing;

      if (
        !action.payload ||
        typeof action.payload.zone !== "string" ||
        !action.payload.zone.trim()
      ) {
        return fail(
          "WORLD_SET_ZONE",
          "INVALID_PAYLOAD",
          "zone must be a non-empty string.",
          state.liveLoop,
        );
      }

      const next = copyLiveLoopState(state.liveLoop);
      setZone(next.world, action.payload.zone.trim());
      next.updatedAt = Date.now();

      return success("WORLD_SET_ZONE", next, {
        zone: next.world.zone,
      });
    }

    case "WORLD_SET_WEATHER": {
      const missing = requireLiveLoop(state, "WORLD_SET_WEATHER");
      if (missing) return missing;

      if (
        !action.payload ||
        typeof action.payload.weather !== "string" ||
        !action.payload.weather.trim()
      ) {
        return fail(
          "WORLD_SET_WEATHER",
          "INVALID_PAYLOAD",
          "weather must be a non-empty string.",
          state.liveLoop,
        );
      }

      const next = copyLiveLoopState(state.liveLoop);
      setWeather(next.world, action.payload.weather.trim());
      next.updatedAt = Date.now();

      return success("WORLD_SET_WEATHER", next, {
        weather: next.world.weather,
      });
    }

    case "BOOTSTRAP":
    case "TICK":
    case "GRANT_COINS":
    case "GRANT_ITEM":
    case "BUY_ITEM":
    case "USE_ITEM":
    case "READ_NOTIFICATION":
    case "READ_ALL_NOTIFICATIONS":
    case "CLEAR_READ_NOTIFICATIONS":
    case "CLAIM_QUEST":
    case "CONSUME_EVENTS":
    case "CLEAR_EVENTS":
    case "SNAPSHOT": {
      const missing = requireLiveLoop(state, action.type);
      if (missing) return missing;

      const response = dispatchSessionAction(
        { session: state.liveLoop.session },
        action,
      );

      return applySessionDispatchToLiveLoop(state.liveLoop, response);
    }

    default: {
      return fail(
        (action as { type: string }).type as TamaLiveLoopActionType,
        "UNKNOWN_ACTION",
        "Unknown live loop action type.",
        hasLiveLoop(state) ? state.liveLoop : undefined,
      );
    }
  }
}
