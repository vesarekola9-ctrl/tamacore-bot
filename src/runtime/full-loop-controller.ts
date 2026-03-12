import {
  createLiveLoop,
  tickLiveLoop,
  type TamaLiveLoopState,
  type TamaLiveLoopTickResult,
} from "./live-loop";

import {
  dispatchLiveLoopAction,
  type TamaAnyLiveLoopAction,
  type TamaLiveLoopDispatchResponse,
} from "./gdevelop-live-loop";

import {
  createUiBridgeSnapshot,
  type TamaUiBridgeSnapshot,
} from "./ui-bridge";

import {
  buildFactorySceneState,
  type FactorySceneState,
} from "./factory-scene-spawn";

import {
  exportLiveLoopStateToGDevelop,
  type TamaGDevelopExport,
} from "./gdevelop-state";

import {
  buildSceneStateFromLiveLoop,
} from "./gdevelop-scene-bindings";

import type { TamaGDevelopSceneState } from "./gdevelop-scene";



export interface TamaFullLoopState {

  liveLoop: TamaLiveLoopState

  gdevelop: TamaGDevelopExport

  scene: TamaGDevelopSceneState

  factoryScene: FactorySceneState

  ui: TamaUiBridgeSnapshot

  lastTick: number

}



export interface TamaFullLoopTickResult {

  state: TamaFullLoopState

  tick: TamaLiveLoopTickResult

}



export interface TamaFullLoopActionResult {

  state: TamaFullLoopState

  response: TamaLiveLoopDispatchResponse

}



function buildFullLoopState(

  liveLoop: TamaLiveLoopState

): TamaFullLoopState {

  const gdevelop = exportLiveLoopStateToGDevelop(liveLoop)

  const scene = buildSceneStateFromLiveLoop(liveLoop)

  const factoryScene = buildFactorySceneState(liveLoop)

  const ui = createUiBridgeSnapshot(liveLoop)



  return {

    liveLoop,

    gdevelop,

    scene,

    factoryScene,

    ui,

    lastTick: Date.now(),

  }

}



export function createFullLoop(): TamaFullLoopState {

  const liveLoop = createLiveLoop()

  return buildFullLoopState(liveLoop)

}



export function snapshotFullLoop(

  state: TamaFullLoopState

): TamaFullLoopState {

  return buildFullLoopState(state.liveLoop)

}



export function tickFullLoop(

  state: TamaFullLoopState,

  now = Date.now()

): TamaFullLoopTickResult {

  const tick = tickLiveLoop(state.liveLoop, now)



  const next = buildFullLoopState(tick.state)



  next.lastTick = now



  return {

    state: next,

    tick,

  }

}



export function dispatchFullLoopAction(

  state: TamaFullLoopState,

  action: TamaAnyLiveLoopAction

): TamaFullLoopActionResult {

  const response = dispatchLiveLoopAction(

    { liveLoop: state.liveLoop },

    action

  )



  const nextLiveLoop = response.ok

    ? response.liveLoop

    : state.liveLoop



  return {

    state: buildFullLoopState(nextLiveLoop),

    response,

  }

}



export function getUiSnapshot(

  state: TamaFullLoopState

): TamaUiBridgeSnapshot {

  return state.ui

}



export function getSceneState(

  state: TamaFullLoopState

): TamaGDevelopSceneState {

  return state.scene

}



export function getFactoryScene(

  state: TamaFullLoopState

): FactorySceneState {

  return state.factoryScene

}



export function getGDevelopExport(

  state: TamaFullLoopState

): TamaGDevelopExport {

  return state.gdevelop

}



export function getLiveLoop(

  state: TamaFullLoopState

): TamaLiveLoopState {

  return state.liveLoop

}
