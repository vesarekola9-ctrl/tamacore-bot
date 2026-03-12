import {
  buildSceneStateFromLiveLoop,
  readScenePetStat,
  readSceneSessionValue,
  readSceneWorldValue,
  listSceneInventoryRows,
  listSceneQuestRows,
  listSceneNotificationRows,
  listSceneCatalogRows,
  listSceneEventRows,
} from "./gdevelop-scene-bindings";
import {
  exportLiveLoopStateToGDevelop,
  type TamaGDevelopExport,
} from "./gdevelop-state";
import {
  dispatchLiveLoopAction,
  type TamaAnyLiveLoopAction,
  type TamaLiveLoopDispatchResponse,
  type TamaLiveLoopState,
} from "./gdevelop-live-loop";
import {
  runGDevelopLiveLoopCommand,
  runGDevelopLiveLoopCommandBatch,
  type TamaGDevelopLiveLoopCommand,
  type TamaGDevelopLiveLoopCommandBatchResult,
} from "./gdevelop-live-loop-commands";
import type { TamaGDevelopSceneState } from "./gdevelop-scene";

export type TamaUiStatKey =
  | "energy"
  | "hunger"
  | "happiness"
  | "hygiene"
  | "health";

export type TamaUiWorldKey =
  | "day"
  | "time"
  | "speed"
  | "zone"
  | "weather"
  | "isNight"
  | "isMorning"
  | "isEvening";

export interface TamaUiStatsModel {
  energy: number;
  hunger: number;
  happiness: number;
  hygiene: number;
  health: number;
}

export interface TamaUiSessionModel {
  coins: number;
  createdAt: number;
  updatedAt: number;
  lastActionAt: number;
}

export interface TamaUiWorldModel {
  day: number;
  time: number;
  speed: number;
  zone: string;
  weather: string;
  isNight: boolean;
  isMorning: boolean;
  isEvening: boolean;
}

export interface TamaUiCountsModel {
  inventory: number;
  quests: number;
  notifications: number;
  catalog: number;
  events: number;
}

export interface TamaUiCollectionsModel {
  inventory: ReturnType<typeof listSceneInventoryRows>;
  quests: ReturnType<typeof listSceneQuestRows>;
  notifications: ReturnType<typeof listSceneNotificationRows>;
  catalog: ReturnType<typeof listSceneCatalogRows>;
  events: ReturnType<typeof listSceneEventRows>;
}

export interface TamaUiBridgeSnapshot {
  liveLoop: TamaLiveLoopState;
  gdevelop: TamaGDevelopExport;
  scene: TamaGDevelopSceneState;
  stats: TamaUiStatsModel;
  session: TamaUiSessionModel;
  world: TamaUiWorldModel;
  counts: TamaUiCountsModel;
  collections: TamaUiCollectionsModel;
}

export interface TamaUiBridgeActionResult {
  snapshot: TamaUiBridgeSnapshot;
  response: TamaLiveLoopDispatchResponse;
}

export interface TamaUiBridgeCommandResult {
  snapshot: TamaUiBridgeSnapshot;
  response: TamaLiveLoopDispatchResponse;
}

export interface TamaUiBridgeCommandBatchResult {
  snapshot: TamaUiBridgeSnapshot;
  batch: TamaGDevelopLiveLoopCommandBatchResult;
}

function safeNumber(value: string | number | boolean | undefined, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function safeString(value: string | number | boolean | undefined, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function safeBoolean(
  value: string | number | boolean | undefined,
  fallback = false,
): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function requireScene(liveLoop: TamaLiveLoopState): TamaGDevelopSceneState {
  const scene = buildSceneStateFromLiveLoop(liveLoop);

  if (!scene) {
    throw new Error("Failed to build scene state from live loop.");
  }

  return scene;
}

function buildStats(scene: TamaGDevelopSceneState): TamaUiStatsModel {
  return {
    energy: safeNumber(readScenePetStat(scene, "Energy")),
    hunger: safeNumber(readScenePetStat(scene, "Hunger")),
    happiness: safeNumber(readScenePetStat(scene, "Happiness")),
    hygiene: safeNumber(readScenePetStat(scene, "Hygiene")),
    health: safeNumber(readScenePetStat(scene, "Health")),
  };
}

function buildSession(scene: TamaGDevelopSceneState): TamaUiSessionModel {
  return {
    coins: safeNumber(readSceneSessionValue(scene, "Coins")),
    createdAt: safeNumber(readSceneSessionValue(scene, "CreatedAt")),
    updatedAt: safeNumber(readSceneSessionValue(scene, "UpdatedAt")),
    lastActionAt: safeNumber(readSceneSessionValue(scene, "LastActionAt")),
  };
}

function buildWorld(scene: TamaGDevelopSceneState): TamaUiWorldModel {
  return {
    day: safeNumber(readSceneWorldValue(scene, "Day"), 1),
    time: safeNumber(readSceneWorldValue(scene, "Time")),
    speed: safeNumber(readSceneWorldValue(scene, "Speed"), 1),
    zone: safeString(readSceneWorldValue(scene, "Zone"), "home"),
    weather: safeString(readSceneWorldValue(scene, "Weather"), "clear"),
    isNight: safeBoolean(readSceneWorldValue(scene, "IsNight")),
    isMorning: safeBoolean(readSceneWorldValue(scene, "IsMorning")),
    isEvening: safeBoolean(readSceneWorldValue(scene, "IsEvening")),
  };
}

function buildCollections(scene: TamaGDevelopSceneState): TamaUiCollectionsModel {
  return {
    inventory: listSceneInventoryRows(scene),
    quests: listSceneQuestRows(scene),
    notifications: listSceneNotificationRows(scene),
    catalog: listSceneCatalogRows(scene),
    events: listSceneEventRows(scene),
  };
}

function buildCounts(collections: TamaUiCollectionsModel): TamaUiCountsModel {
  return {
    inventory: collections.inventory.length,
    quests: collections.quests.length,
    notifications: collections.notifications.length,
    catalog: collections.catalog.length,
    events: collections.events.length,
  };
}

export function createUiBridgeSnapshot(
  liveLoop: TamaLiveLoopState,
): TamaUiBridgeSnapshot {
  const gdevelop = exportLiveLoopStateToGDevelop(liveLoop);
  const scene = requireScene(liveLoop);
  const collections = buildCollections(scene);

  return {
    liveLoop,
    gdevelop,
    scene,
    stats: buildStats(scene),
    session: buildSession(scene),
    world: buildWorld(scene),
    counts: buildCounts(collections),
    collections,
  };
}

export function dispatchUiBridgeAction(
  liveLoop: TamaLiveLoopState,
  action: TamaAnyLiveLoopAction,
): TamaUiBridgeActionResult {
  const response = dispatchLiveLoopAction({ liveLoop }, action);
  const nextLiveLoop = response.ok ? response.liveLoop : liveLoop;

  return {
    snapshot: createUiBridgeSnapshot(nextLiveLoop),
    response,
  };
}

export function runUiBridgeCommand(
  liveLoop: TamaLiveLoopState,
  command: TamaGDevelopLiveLoopCommand,
): TamaUiBridgeCommandResult {
  const response = runGDevelopLiveLoopCommand({ liveLoop }, command);
  const nextLiveLoop = response.ok ? response.liveLoop : liveLoop;

  return {
    snapshot: createUiBridgeSnapshot(nextLiveLoop),
    response,
  };
}

export function runUiBridgeCommandBatch(
  liveLoop: TamaLiveLoopState,
  commands: TamaGDevelopLiveLoopCommand[],
): TamaUiBridgeCommandBatchResult {
  const batch = runGDevelopLiveLoopCommandBatch({ liveLoop }, commands);
  const nextLiveLoop = batch.state.liveLoop ?? liveLoop;

  return {
    snapshot: createUiBridgeSnapshot(nextLiveLoop),
    batch,
  };
}

export function readUiStat(
  snapshot: TamaUiBridgeSnapshot,
  key: TamaUiStatKey,
): number {
  return snapshot.stats[key];
}

export function readUiWorld(
  snapshot: TamaUiBridgeSnapshot,
  key: TamaUiWorldKey,
): string | number | boolean {
  return snapshot.world[key];
}
