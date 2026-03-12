import {
  createFullLoop,
  tickFullLoop,
  type TamaFullLoopState,
} from "./full-loop-controller";

import {
  createAiControllerState,
  runAiStep,
  type TamaAiControllerState,
} from "./ai-bot-controller";

export interface TamaRuntimeInstance {

  loop: TamaFullLoopState

  ai: TamaAiControllerState

  running: boolean

  lastUpdate: number

}



export function createRuntime(): TamaRuntimeInstance {

  return {

    loop: createFullLoop(),

    ai: createAiControllerState(),

    running: false,

    lastUpdate: Date.now(),

  }

}



export function startRuntime(runtime: TamaRuntimeInstance) {

  runtime.running = true

  runtime.lastUpdate = Date.now()

}



export function stopRuntime(runtime: TamaRuntimeInstance) {

  runtime.running = false

}



export function stepRuntime(

  runtime: TamaRuntimeInstance,

  now = Date.now()

): TamaRuntimeInstance {

  if (!runtime.running) {

    return runtime

  }

  const tick = tickFullLoop(runtime.loop, now)

  const ai = runAiStep(tick.state, runtime.ai, now)

  return {

    loop: ai.loop,

    ai: ai.ai,

    running: runtime.running,

    lastUpdate: now,

  }

}



export function getRuntimeLoop(

  runtime: TamaRuntimeInstance

): TamaFullLoopState {

  return runtime.loop

}



export function getRuntimeUi(

  runtime: TamaRuntimeInstance

) {

  return runtime.loop.ui

}
