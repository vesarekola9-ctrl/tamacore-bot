import {
  dispatchLiveLoopAction,
  type TamaAnyLiveLoopAction,
  type TamaLiveLoopDispatchResponse,
  type TamaLiveLoopDispatchState,
} from "./gdevelop-live-loop";

import {
  exportLiveLoopStateToGDevelop,
  type TamaGDevelopExport,
} from "./gdevelop-state";


export interface TamaGDevelopLiveLoopCommand {

  action: string

  now?: number

  itemId?: string

  quantity?: number

  amount?: number

  id?: string

  questId?: string

  count?: number

  zone?: string

  weather?: string

}


export interface TamaGDevelopLiveLoopCommandResult {

  state: TamaLiveLoopDispatchState

  response: TamaLiveLoopDispatchResponse

  gdevelop?: TamaGDevelopExport

}


export interface TamaGDevelopLiveLoopCommandBatchResult {

  state: TamaLiveLoopDispatchState

  responses: TamaLiveLoopDispatchResponse[]

  gdevelop?: TamaGDevelopExport

}



function safeNumber(v: unknown): number | undefined {

  return typeof v === "number" && Number.isFinite(v)

    ? v

    : undefined

}


function safeString(v: unknown): string | undefined {

  return typeof v === "string" && v.length > 0

    ? v

    : undefined

}



function mapCommand(

  cmd: TamaGDevelopLiveLoopCommand

): TamaAnyLiveLoopAction | undefined {

  const action = safeString(cmd.action)



  switch (action) {

    case "LIVE_BOOTSTRAP":

      return {

        type: "LIVE_BOOTSTRAP",

        payload: {

          now: safeNumber(cmd.now),

        },

      }



    case "LIVE_TICK":

      return {

        type: "LIVE_TICK",

        payload: {

          now: safeNumber(cmd.now),

        },

      }



    case "LIVE_SNAPSHOT":

      return {

        type: "LIVE_SNAPSHOT",

      }



    case "WORLD_SET_ZONE":

      if (!safeString(cmd.zone)) return undefined

      return {

        type: "WORLD_SET_ZONE",

        payload: {

          zone: cmd.zone as string,

        },

      }



    case "WORLD_SET_WEATHER":

      if (!safeString(cmd.weather)) return undefined

      return {

        type: "WORLD_SET_WEATHER",

        payload: {

          weather: cmd.weather as string,

        },

      }



    case "GRANT_COINS":

      if (safeNumber(cmd.amount) === undefined) return undefined

      return {

        type: "GRANT_COINS",

        payload: {

          amount: cmd.amount as number,

          now: safeNumber(cmd.now),

        },

      }



    case "GRANT_ITEM":

      if (!safeString(cmd.itemId)) return undefined

      return {

        type: "GRANT_ITEM",

        payload: {

          itemId: cmd.itemId as string,

          quantity: safeNumber(cmd.quantity),

          now: safeNumber(cmd.now),

        },

      }



    case "BUY_ITEM":

      if (!safeString(cmd.itemId)) return undefined

      return {

        type: "BUY_ITEM",

        payload: {

          itemId: cmd.itemId as string,

          now: safeNumber(cmd.now),

        },

      }



    case "USE_ITEM":

      if (!safeString(cmd.itemId)) return undefined

      return {

        type: "USE_ITEM",

        payload: {

          itemId: cmd.itemId as string,

          now: safeNumber(cmd.now),

        },

      }



    case "READ_NOTIFICATION":

      if (!safeString(cmd.id)) return undefined

      return {

        type: "READ_NOTIFICATION",

        payload: {

          id: cmd.id as string,

          now: safeNumber(cmd.now),

        },

      }



    case "CLAIM_QUEST":

      if (!safeString(cmd.questId)) return undefined

      return {

        type: "CLAIM_QUEST",

        payload: {

          questId: cmd.questId as string,

          now: safeNumber(cmd.now),

        },

      }



    case "CONSUME_EVENTS":

      return {

        type: "CONSUME_EVENTS",

        payload: {

          count: safeNumber(cmd.count),

          now: safeNumber(cmd.now),

        },

      }



    case "CLEAR_EVENTS":

      return {

        type: "CLEAR_EVENTS",

        payload: {

          now: safeNumber(cmd.now),

        },

      }



    default:

      return undefined

  }

}



export function runGDevelopLiveLoopCommand(

  state: TamaLiveLoopDispatchState,

  command: TamaGDevelopLiveLoopCommand

): TamaGDevelopLiveLoopCommandResult {



  const action = mapCommand(command)



  if (!action) {

    return {

      state,

      response: {

        ok: false,

        action: command.action as never,

        code: "INVALID_ACTION",

        error: "Invalid command",

      },

    }

  }



  const response = dispatchLiveLoopAction(state, action)



  const nextState = response.ok

    ? { liveLoop: response.liveLoop }

    : state



  return {

    state: nextState,

    response,

    gdevelop: response.ok

      ? exportLiveLoopStateToGDevelop(response.liveLoop)

      : undefined,

  }

}



export function runGDevelopLiveLoopCommandBatch(

  initial: TamaLiveLoopDispatchState,

  commands: TamaGDevelopLiveLoopCommand[]

): TamaGDevelopLiveLoopCommandBatchResult {



  let state: TamaLiveLoopDispatchState = {

    liveLoop: initial.liveLoop,

  }



  const responses: TamaLiveLoopDispatchResponse[] = []



  for (const cmd of commands) {

    const result = runGDevelopLiveLoopCommand(state, cmd)

    responses.push(result.response)

    state = result.state

  }



  return {

    state,

    responses,

    gdevelop: state.liveLoop

      ? exportLiveLoopStateToGDevelop(state.liveLoop)

      : undefined,

  }

}
