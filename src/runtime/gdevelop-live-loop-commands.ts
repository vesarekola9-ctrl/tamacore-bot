import {
  dispatchLiveLoopAction,
  type TamaAnyLiveLoopAction,
  type TamaLiveLoopActionType,
  type TamaLiveLoopDispatchResponse,
  type TamaLiveLoopDispatchState,
} from "./gdevelop-live-loop";

export interface TamaGDevelopLiveLoopCommand {
  action: TamaLiveLoopActionType | string;
  now?: number;
  itemId?: string;
  quantity?: number;
  amount?: number;
  id?: string;
  questId?: string;
  count?: number;
  zone?: string;
  weather?: string;
}

export interface TamaGDevelopLiveLoopCommandBatchResult {
  state: TamaLiveLoopDispatchState;
  responses: TamaLiveLoopDispatchResponse[];
}

function safeNumber(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function safeString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim().length > 0
    ? value.trim()
    : undefined;
}

export function mapGDevelopLiveLoopCommandToAction(
  command: TamaGDevelopLiveLoopCommand,
): TamaAnyLiveLoopAction | undefined {
  const action = safeString(command.action);

  switch (action) {
    case "LIVE_BOOTSTRAP":
      return {
        type: "LIVE_BOOTSTRAP",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "LIVE_TICK":
      return {
        type: "LIVE_TICK",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "LIVE_SNAPSHOT":
      return {
        type: "LIVE_SNAPSHOT",
      };

    case "WORLD_SET_ZONE":
      if (!safeString(command.zone)) return undefined;
      return {
        type: "WORLD_SET_ZONE",
        payload: {
          zone: command.zone as string,
        },
      };

    case "WORLD_SET_WEATHER":
      if (!safeString(command.weather)) return undefined;
      return {
        type: "WORLD_SET_WEATHER",
        payload: {
          weather: command.weather as string,
        },
      };

    case "BOOTSTRAP":
      return {
        type: "BOOTSTRAP",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "TICK":
      return {
        type: "TICK",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "GRANT_COINS":
      if (safeNumber(command.amount) === undefined) return undefined;
      return {
        type: "GRANT_COINS",
        payload: {
          amount: command.amount as number,
          now: safeNumber(command.now),
        },
      };

    case "GRANT_ITEM":
      if (!safeString(command.itemId)) return undefined;
      return {
        type: "GRANT_ITEM",
        payload: {
          itemId: command.itemId as string,
          quantity: safeNumber(command.quantity),
          now: safeNumber(command.now),
        },
      };

    case "BUY_ITEM":
      if (!safeString(command.itemId)) return undefined;
      return {
        type: "BUY_ITEM",
        payload: {
          itemId: command.itemId as string,
          now: safeNumber(command.now),
        },
      };

    case "USE_ITEM":
      if (!safeString(command.itemId)) return undefined;
      return {
        type: "USE_ITEM",
        payload: {
          itemId: command.itemId as string,
          now: safeNumber(command.now),
        },
      };

    case "READ_NOTIFICATION":
      if (!safeString(command.id)) return undefined;
      return {
        type: "READ_NOTIFICATION",
        payload: {
          id: command.id as string,
          now: safeNumber(command.now),
        },
      };

    case "READ_ALL_NOTIFICATIONS":
      return {
        type: "READ_ALL_NOTIFICATIONS",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "CLEAR_READ_NOTIFICATIONS":
      return {
        type: "CLEAR_READ_NOTIFICATIONS",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "CLAIM_QUEST":
      if (!safeString(command.questId)) return undefined;
      return {
        type: "CLAIM_QUEST",
        payload: {
          questId: command.questId as string,
          now: safeNumber(command.now),
        },
      };

    case "CONSUME_EVENTS":
      return {
        type: "CONSUME_EVENTS",
        payload: {
          count: safeNumber(command.count),
          now: safeNumber(command.now),
        },
      };

    case "CLEAR_EVENTS":
      return {
        type: "CLEAR_EVENTS",
        payload: {
          now: safeNumber(command.now),
        },
      };

    case "SNAPSHOT":
      return {
        type: "SNAPSHOT",
      };

    default:
      return undefined;
  }
}

export function runGDevelopLiveLoopCommand(
  state: TamaLiveLoopDispatchState,
  command: TamaGDevelopLiveLoopCommand,
): TamaLiveLoopDispatchResponse {
  const action = mapGDevelopLiveLoopCommandToAction(command);

  if (!action) {
    return {
      ok: false,
      action: (safeString(command.action) ?? "LIVE_SNAPSHOT") as TamaLiveLoopActionType,
      code: "INVALID_ACTION",
      error: "Could not map GDevelop live loop command to runtime action.",
      liveLoop: state.liveLoop,
      gdevelop: state.liveLoop ? undefined : undefined,
    };
  }

  return dispatchLiveLoopAction(state, action);
}

export function runGDevelopLiveLoopCommandBatch(
  initialState: TamaLiveLoopDispatchState,
  commands: TamaGDevelopLiveLoopCommand[],
): TamaGDevelopLiveLoopCommandBatchResult {
  let state: TamaLiveLoopDispatchState = {
    liveLoop: initialState.liveLoop,
  };

  const responses: TamaLiveLoopDispatchResponse[] = [];

  for (const command of commands) {
    const response = runGDevelopLiveLoopCommand(state, command);
    responses.push(response);

    if (response.ok) {
      state = {
        liveLoop: response.liveLoop,
      };
    }
  }

  return {
    state,
    responses,
  };
}
