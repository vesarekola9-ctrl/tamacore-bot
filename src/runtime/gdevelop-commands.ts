import {
  dispatchSessionActionForGDevelop,
  type TamaGDevelopDispatchResponse,
} from "./gdevelop-actions";
import type {
  TamaDispatchAction,
  TamaDispatchActionType,
  TamaDispatchState,
} from "./dispatcher";

export interface TamaGDevelopCommand {
  action: TamaDispatchActionType | string;
  now?: number;
  itemId?: string;
  quantity?: number;
  amount?: number;
  id?: string;
  questId?: string;
  count?: number;
}

export interface TamaGDevelopCommandBatchResult {
  state: TamaDispatchState;
  responses: TamaGDevelopDispatchResponse[];
}

function safeNumber(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) ? value : undefined;
}

function safeString(value: unknown): string | undefined {
  return typeof value === "string" && value.length > 0 ? value : undefined;
}

export function mapGDevelopCommandToAction(
  command: TamaGDevelopCommand,
): TamaDispatchAction | undefined {
  const action = safeString(command.action);

  switch (action) {
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

export function runGDevelopCommand(
  state: TamaDispatchState,
  command: TamaGDevelopCommand,
): TamaGDevelopDispatchResponse {
  const action = mapGDevelopCommandToAction(command);

  if (!action) {
    return {
      ok: false,
      action: safeString(command.action) as TamaDispatchActionType,
      code: "INVALID_ACTION",
      error: "Could not map GDevelop command to runtime action.",
      session: state.session,
    };
  }

  return dispatchSessionActionForGDevelop(state, action);
}

export function runGDevelopCommandBatch(
  initialState: TamaDispatchState,
  commands: TamaGDevelopCommand[],
): TamaGDevelopCommandBatchResult {
  let state: TamaDispatchState = {
    session: initialState.session,
  };

  const responses: TamaGDevelopDispatchResponse[] = [];

  for (const command of commands) {
    const response = runGDevelopCommand(state, command);
    responses.push(response);

    if (response.ok) {
      state = {
        session: response.session,
      };
    }
  }

  return {
    state,
    responses,
  };
}
