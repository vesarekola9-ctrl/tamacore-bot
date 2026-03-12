import {
  createGDevelopState,
  dispatchSessionActionForGDevelop,
  type TamaGDevelopDispatchResponse,
} from "./gdevelop-actions";
import {
  createSceneStateFromSnapshotExport,
  findSceneRowById,
  getSceneRowsByCollection,
  getSceneVariableValue,
  type TamaGDevelopSceneArrayRow,
  type TamaGDevelopSceneState,
} from "./gdevelop-scene";
import type { TamaDispatchAction, TamaDispatchState } from "./dispatcher";
import type { TamaSessionState } from "./session";

export interface TamaSceneBindingResult {
  response: TamaGDevelopDispatchResponse;
  scene?: TamaGDevelopSceneState;
}

export function buildSceneStateFromSession(
  session?: TamaSessionState,
): TamaGDevelopSceneState | undefined {
  const exported = createGDevelopState(session);
  return exported ? createSceneStateFromSnapshotExport(exported) : undefined;
}

export function dispatchSceneAction(
  state: TamaDispatchState,
  action: TamaDispatchAction,
): TamaSceneBindingResult {
  const response = dispatchSessionActionForGDevelop(state, action);

  if (!response.ok || !response.gdevelop) {
    return { response };
  }

  return {
    response,
    scene: createSceneStateFromSnapshotExport(response.gdevelop),
  };
}

export function readScenePetStat(
  scene: TamaGDevelopSceneState,
  stat: "Energy" | "Hunger" | "Happiness" | "Hygiene" | "Health",
): string | number | boolean | undefined {
  return getSceneVariableValue(scene, `Pet.${stat}`);
}

export function readSceneSessionValue(
  scene: TamaGDevelopSceneState,
  key: "Coins" | "CreatedAt" | "UpdatedAt" | "LastActionAt",
): string | number | boolean | undefined {
  return getSceneVariableValue(scene, `Session.${key}`);
}

export function listSceneInventoryRows(
  scene: TamaGDevelopSceneState,
): TamaGDevelopSceneArrayRow[] {
  return getSceneRowsByCollection(scene, "inventory");
}

export function listSceneQuestRows(
  scene: TamaGDevelopSceneState,
): TamaGDevelopSceneArrayRow[] {
  return getSceneRowsByCollection(scene, "quests");
}

export function listSceneNotificationRows(
  scene: TamaGDevelopSceneState,
): TamaGDevelopSceneArrayRow[] {
  return getSceneRowsByCollection(scene, "notifications");
}

export function listSceneCatalogRows(
  scene: TamaGDevelopSceneState,
): TamaGDevelopSceneArrayRow[] {
  return getSceneRowsByCollection(scene, "catalog");
}

export function listSceneEventRows(
  scene: TamaGDevelopSceneState,
): TamaGDevelopSceneArrayRow[] {
  return getSceneRowsByCollection(scene, "events");
}

export function findSceneInventoryItem(
  scene: TamaGDevelopSceneState,
  itemId: string,
): TamaGDevelopSceneArrayRow | undefined {
  return findSceneRowById(scene.inventory, itemId);
}

export function findSceneQuest(
  scene: TamaGDevelopSceneState,
  questId: string,
): TamaGDevelopSceneArrayRow | undefined {
  return findSceneRowById(scene.quests, questId);
}

export function findSceneNotification(
  scene: TamaGDevelopSceneState,
  notificationId: string,
): TamaGDevelopSceneArrayRow | undefined {
  return findSceneRowById(scene.notifications, notificationId);
}

export function findSceneCatalogItem(
  scene: TamaGDevelopSceneState,
  itemId: string,
): TamaGDevelopSceneArrayRow | undefined {
  return findSceneRowById(scene.catalog, itemId);
}
