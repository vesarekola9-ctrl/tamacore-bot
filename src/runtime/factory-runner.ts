import {
  createRuntime,
  startRuntime,
  stepRuntime,
  getRuntimeLoop,
  getRuntimeUi,
  type TamaRuntimeInstance,
} from "./runtime-bootstrap";

import {
  createFactoryExport,
  tickFactoryExport,
  type TamaFactoryExportState,
} from "./factory-export";

import {
  buildFactorySceneState,
  type FactorySceneState,
} from "./factory-scene-spawn";

import {
  createUiBridgeSnapshot,
  type TamaUiBridgeSnapshot,
} from "./ui-bridge";

import type { TamaFullLoopState } from "./full-loop-controller";



export interface TamaFactoryRunnerState {

  runtime: TamaRuntimeInstance

  export: TamaFactoryExportState

  scene: FactorySceneState

  ui: TamaUiBridgeSnapshot

  started: boolean

  lastUpdate: number

}



export interface TamaFactoryRunnerStepResult {

  state: TamaFactoryRunnerState

}



function buildRunnerState(

  runtime: TamaRuntimeInstance,

  exp: TamaFactoryExportState

): TamaFactoryRunnerState {

  const loop: TamaFullLoopState = getRuntimeLoop(runtime)

  const scene = buildFactorySceneState(loop.liveLoop)

  const ui = createUiBridgeSnapshot(loop.liveLoop)

  return {

    runtime,

    export: exp,

    scene,

    ui,

    started: true,

    lastUpdate: Date.now(),

  }

}



export function createFactoryRunner(): TamaFactoryRunnerState {

  const runtime = createRuntime()

  const exp = createFactoryExport()

  return buildRunnerState(runtime, exp)

}



export function startFactoryRunner(

  state: TamaFactoryRunnerState

): TamaFactoryRunnerState {

  const runtime = startRuntime(state.runtime)

  return buildRunnerState(runtime, state.export)

}



export function stepFactoryRunner(

  state: TamaFactoryRunnerState,

  now = Date.now()

): TamaFactoryRunnerStepResult {

  const runtimeStep = stepRuntime(state.runtime, now)

  const exportStep = tickFactoryExport(

    state.export,

    now

  )

  const next = buildRunnerState(

    runtimeStep.runtime,

    exportStep.state

  )

  next.lastUpdate = now

  return {

    state: next,

  }

}



export function getRunnerRuntime(

  state: TamaFactoryRunnerState

): TamaRuntimeInstance {

  return state.runtime

}



export function getRunnerUi(

  state: TamaFactoryRunnerState

): TamaUiBridgeSnapshot {

  return state.ui

}



export function getRunnerScene(

  state: TamaFactoryRunnerState

): FactorySceneState {

  return state.scene

}



export function getRunnerExport(

  state: TamaFactoryRunnerState

): TamaFactoryExportState {

  return state.export

}
