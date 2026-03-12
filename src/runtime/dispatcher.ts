import {
  bootstrapBridgeSession,
  bridgeBuyItem,
  bridgeClaimQuest,
  bridgeClearEvents,
  bridgeClearReadNotifications,
  bridgeConsumeEvents,
  bridgeGrantCoins,
  bridgeGrantItem,
  bridgeReadAllNotifications,
  bridgeReadNotification,
  bridgeTickSession,
  bridgeUseItem,
  createBridgeSnapshot,
  type TamaBridgeBootstrapInput,
  type TamaBridgeResult,
  type TamaBridgeSnapshot,
} from "./bridge";
import type { TamaNeedDecayRates } from "./pet-state";
import type { TamaSessionState } from "./session";

export type TamaDispatchActionType =
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

export interface TamaBootstrapAction {
  type: "BOOTSTRAP";
  payload?: TamaBridgeBootstrapInput;
}

export interface TamaTickAction {
  type: "TICK";
  payload?: {
    now?: number;
    decayRates?: Partial<TamaNeedDecayRates>;
  };
}

export interface TamaGrantCoinsAction {
  type: "GRANT_COINS";
  payload: {
    amount: number;
    now?: number;
  };
}

export interface TamaGrantItemAction {
  type: "GRANT_ITEM";
  payload: {
    itemId: string;
    quantity?: number;
    now?: number;
  };
}

export interface TamaBuyItemAction {
  type: "BUY_ITEM";
  payload: {
    itemId: string;
    now?: number;
  };
}

export interface TamaUseItemAction {
  type: "USE_ITEM";
  payload: {
    itemId: string;
    now?: number;
  };
}

export interface TamaReadNotificationAction {
  type: "READ_NOTIFICATION";
  payload: {
    id: string;
    now?: number;
  };
}

export interface TamaReadAllNotificationsAction {
  type: "READ_ALL_NOTIFICATIONS";
  payload?: {
    now?: number;
  };
}

export interface TamaClearReadNotificationsAction {
  type: "CLEAR_READ_NOTIFICATIONS";
  payload?: {
    now?: number;
  };
}

export interface TamaClaimQuestAction {
  type: "CLAIM_QUEST";
  payload: {
    questId: string;
    now?: number;
  };
}

export interface TamaConsumeEventsAction {
  type: "CONSUME_EVENTS";
  payload?: {
    count?: number;
    now?: number;
  };
}

export interface TamaClearEventsAction {
  type: "CLEAR_EVENTS";
  payload?: {
    now?: number;
  };
}

export interface TamaSnapshotAction {
  type: "SNAPSHOT";
}

export type TamaDispatchAction =
  | TamaBootstrapAction
  | TamaTickAction
  | TamaGrantCoinsAction
  | TamaGrantItemAction
  | TamaBuyItemAction
  | TamaUseItemAction
  | TamaReadNotificationAction
  | TamaReadAllNotificationsAction
  | TamaClearReadNotificationsAction
  | TamaClaimQuestAction
  | TamaConsumeEventsAction
  | TamaClearEventsAction
  | TamaSnapshotAction;

export interface TamaDispatchState {
  session?: TamaSessionState;
}

export interface TamaDispatchSuccess<T = Record<string, unknown>> {
  ok: true;
  action: TamaDispatchActionType;
  session: TamaSessionState;
  snapshot: TamaBridgeSnapshot;
  result: T;
}

export interface TamaDispatchFailure {
  ok: false;
  action: TamaDispatchActionType;
  error: string;
  code:
    | "SESSION_REQUIRED"
    | "INVALID_ACTION"
    | "INVALID_PAYLOAD"
    | "UNKNOWN_ACTION";
  session?: TamaSessionState;
  snapshot?: TamaBridgeSnapshot;
}

export type TamaDispatchResponse<T = Record<string, unknown>> =
  | TamaDispatchSuccess<T>
  | TamaDispatchFailure;

function hasSession(state: TamaDispatchState): state is { session: TamaSessionState } {
  return !!state.session;
}

function successFromBridge<T>(
  action: TamaDispatchActionType,
  bridge: TamaBridgeResult<T>,
): TamaDispatchSuccess<T> {
  return {
    ok: true,
    action,
    session: bridge.session,
    snapshot: bridge.snapshot,
    result: bridge.result,
  };
}

function failure(
  action: TamaDispatchActionType,
  code: TamaDispatchFailure["code"],
  error: string,
  session?: TamaSessionState,
): TamaDispatchFailure {
  return {
    ok: false,
    action,
    code,
    error,
    session,
    snapshot: session ? createBridgeSnapshot(session) : undefined,
  };
}

function requireSession(
  state: TamaDispatchState,
  action: TamaDispatchActionType,
): TamaDispatchFailure | null {
  if (!hasSession(state)) {
    return failure(action, "SESSION_REQUIRED", "Session has not been initialized.");
  }
  return null;
}

export function dispatchSessionAction(
  state: TamaDispatchState,
  action: TamaDispatchAction,
): TamaDispatchResponse {
  switch (action.type) {
    case "BOOTSTRAP": {
      const bridge = bootstrapBridgeSession(action.payload);
      return successFromBridge("BOOTSTRAP", bridge);
    }

    case "TICK": {
      const missing = requireSession(state, "TICK");
      if (missing) return missing;

      const bridge = bridgeTickSession(
        state.session,
        action.payload?.now ?? Date.now(),
        action.payload?.decayRates,
      );

      return successFromBridge("TICK", bridge);
    }

    case "GRANT_COINS": {
      const missing = requireSession(state, "GRANT_COINS");
      if (missing) return missing;

      if (!action.payload || typeof action.payload.amount !== "number") {
        return failure(
          "GRANT_COINS",
          "INVALID_PAYLOAD",
          "amount must be a finite number.",
          state.session,
        );
      }

      const bridge = bridgeGrantCoins(
        state.session,
        action.payload.amount,
        action.payload.now ?? Date.now(),
      );

      return successFromBridge("GRANT_COINS", bridge);
    }

    case "GRANT_ITEM": {
      const missing = requireSession(state, "GRANT_ITEM");
      if (missing) return missing;

      if (!action.payload || typeof action.payload.itemId !== "string") {
        return failure(
          "GRANT_ITEM",
          "INVALID_PAYLOAD",
          "itemId must be a non-empty string.",
          state.session,
        );
      }

      const bridge = bridgeGrantItem(
        state.session,
        action.payload.itemId,
        action.payload.quantity ?? 1,
        action.payload.now ?? Date.now(),
      );

      return successFromBridge("GRANT_ITEM", bridge);
    }

    case "BUY_ITEM": {
      const missing = requireSession(state, "BUY_ITEM");
      if (missing) return missing;

      if (!action.payload || typeof action.payload.itemId !== "string") {
        return failure(
          "BUY_ITEM",
          "INVALID_PAYLOAD",
          "itemId must be a non-empty string.",
          state.session,
        );
      }

      const bridge = bridgeBuyItem(
        state.session,
        action.payload.itemId,
        action.payload.now ?? Date.now(),
      );

      return successFromBridge("BUY_ITEM", bridge);
    }

    case "USE_ITEM": {
      const missing = requireSession(state, "USE_ITEM");
      if (missing) return missing;

      if (!action.payload || typeof action.payload.itemId !== "string") {
        return failure(
          "USE_ITEM",
          "INVALID_PAYLOAD",
          "itemId must be a non-empty string.",
          state.session,
        );
      }

      const bridge = bridgeUseItem(
        state.session,
        action.payload.itemId,
        action.payload.now ?? Date.now(),
      );

      return successFromBridge("USE_ITEM", bridge);
    }

    case "READ_NOTIFICATION": {
      const missing = requireSession(state, "READ_NOTIFICATION");
      if (missing) return missing;

      if (!action.payload || typeof action.payload.id !== "string") {
        return failure(
          "READ_NOTIFICATION",
          "INVALID_PAYLOAD",
          "id must be a non-empty string.",
          state.session,
        );
      }

      const bridge = bridgeReadNotification(
        state.session,
        action.payload.id,
        action.payload.now ?? Date.now(),
      );

      return successFromBridge("READ_NOTIFICATION", bridge);
    }

    case "READ_ALL_NOTIFICATIONS": {
      const missing = requireSession(state, "READ_ALL_NOTIFICATIONS");
      if (missing) return missing;

      const bridge = bridgeReadAllNotifications(
        state.session,
        action.payload?.now ?? Date.now(),
      );

      return successFromBridge("READ_ALL_NOTIFICATIONS", bridge);
    }

    case "CLEAR_READ_NOTIFICATIONS": {
      const missing = requireSession(state, "CLEAR_READ_NOTIFICATIONS");
      if (missing) return missing;

      const bridge = bridgeClearReadNotifications(
        state.session,
        action.payload?.now ?? Date.now(),
      );

      return successFromBridge("CLEAR_READ_NOTIFICATIONS", bridge);
    }

    case "CLAIM_QUEST": {
      const missing = requireSession(state, "CLAIM_QUEST");
      if (missing) return missing;

      if (!action.payload || typeof action.payload.questId !== "string") {
        return failure(
          "CLAIM_QUEST",
          "INVALID_PAYLOAD",
          "questId must be a non-empty string.",
          state.session,
        );
      }

      const bridge = bridgeClaimQuest(
        state.session,
        action.payload.questId,
        action.payload.now ?? Date.now(),
      );

      return successFromBridge("CLAIM_QUEST", bridge);
    }

    case "CONSUME_EVENTS": {
      const missing = requireSession(state, "CONSUME_EVENTS");
      if (missing) return missing;

      const bridge = bridgeConsumeEvents(
        state.session,
        action.payload?.count ?? 1,
        action.payload?.now ?? Date.now(),
      );

      return successFromBridge("CONSUME_EVENTS", bridge);
    }

    case "CLEAR_EVENTS": {
      const missing = requireSession(state, "CLEAR_EVENTS");
      if (missing) return missing;

      const bridge = bridgeClearEvents(
        state.session,
        action.payload?.now ?? Date.now(),
      );

      return successFromBridge("CLEAR_EVENTS", bridge);
    }

    case "SNAPSHOT": {
      const missing = requireSession(state, "SNAPSHOT");
      if (missing) return missing;

      return {
        ok: true,
        action: "SNAPSHOT",
        session: state.session,
        snapshot: createBridgeSnapshot(state.session),
        result: {},
      };
    }

    default: {
      return failure(
        (action as TamaDispatchAction).type,
        "UNKNOWN_ACTION",
        "Unknown action type.",
        hasSession(state) ? state.session : undefined,
      );
    }
  }
}
