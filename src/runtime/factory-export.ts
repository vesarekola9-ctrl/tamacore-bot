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
  runGDevelopLiveLoopCommand,
  runGDevelopLiveLoopCommandBatch,
  type TamaGDevelopLiveLoopCommand,
  type TamaGDevelopLiveLoopCommandBatchResult,
} from "./gdevelop-live-loop-commands";
import {
  exportLiveLoopStateToGDevelop,
  type TamaGDevelopExport,
} from "./gdevelop-state";
import { buildSceneStateFromLiveLoop } from "./gdevelop-scene-bindings";
import type { TamaGDevelopSceneState } from "./gdevelop-scene";
import type { TamaBridgeBootstrapInput } from "./bridge";
import type { TamaRuntimeBootstrapConfigFile } from "./runtime-config";
import type { TamaWorldBootstrapInput } from "./world";

export interface TamaFactoryExportState {
  liveLoop: TamaLiveLoopState;
  gdevelop: TamaGDevelopExport;
  scene?: TamaGDevelopSceneState;
}

export interface TamaFactoryExportBootstrapInput
  extends TamaBridgeBootstrapInput,
    TamaRuntimeBootstrapConfigFile {
  world?: TamaWorldBootstrapInput;
}

export interface TamaFactoryExportTickResult {
  state: TamaFactoryExportState;
  tick: TamaLiveLoopTickResult;
}

export interface TamaFactoryExportActionResult {
  state: TamaFactoryExportState;
  response: TamaLiveLoopDispatchResponse;
}

export interface TamaFactoryExportCommandResult {
  state: TamaFactoryExportState;
  response: TamaLiveLoopDispatchResponse;
}

export interface TamaFactoryExportCommandBatchResult {
  state: TamaFactoryExportState;
  batch: TamaGDevelopLiveLoopCommandBatchResult;
}

function buildFactoryExportState(
  liveLoop: TamaLiveLoopState,
): TamaFactoryExportState {
  return {
    liveLoop,
    gdevelop: exportLiveLoopStateToGDevelop(liveLoop),
    scene: buildSceneStateFromLiveLoop(liveLoop),
  };
}

export function createFactoryExport(
  input?: TamaFactoryExportBootstrapInput,
): TamaFactoryExportState {
  return buildFactoryExportState(createLiveLoop(input));
}

export function snapshotFactoryExport(
  state: TamaFactoryExportState,
): TamaFactoryExportState {
  return buildFactoryExportState(state.liveLoop);
}

export function tickFactoryExport(
  state: TamaFactoryExportState,
  now = Date.now(),
): TamaFactoryExportTickResult {
  const tick = tickLiveLoop(state.liveLoop, now);

  return {
    state: buildFactoryExportState(tick.state),
    tick,
  };
}

export function dispatchFactoryExportAction(
  state: TamaFactoryExportState,
  action: TamaAnyLiveLoopAction,
): TamaFactoryExportActionResult {
  const response = dispatchLiveLoopAction(
    { liveLoop: state.liveLoop },
    action,
  );

  return {
    state: response.ok
      ? buildFactoryExportState(response.liveLoop)
      : snapshotFactoryExport(state),
    response,
  };
}

export function runFactoryExportCommand(
  state: TamaFactoryExportState,
  command: TamaGDevelopLiveLoopCommand,
): TamaFactoryExportCommandResult {
  const response = runGDevelopLiveLoopCommand(
    { liveLoop: state.liveLoop },
    command,
  );

  return {
    state: response.ok
      ? buildFactoryExportState(response.liveLoop)
      : snapshotFactoryExport(state),
    response,
  };
}

export function runFactoryExportCommandBatch(
  state: TamaFactoryExportState,
  commands: TamaGDevelopLiveLoopCommand[],
): TamaFactoryExportCommandBatchResult {
  const batch = runGDevelopLiveLoopCommandBatch(
    { liveLoop: state.liveLoop },
    commands,
  );

  return {
    state: batch.state.liveLoop
      ? buildFactoryExportState(batch.state.liveLoop)
      : snapshotFactoryExport(state),
    batch,
  };
}
