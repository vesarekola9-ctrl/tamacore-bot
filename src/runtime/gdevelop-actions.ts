import {
  dispatchSessionAction,
  type TamaDispatchAction,
  type TamaDispatchResponse,
  type TamaDispatchState,
} from "./dispatcher";
import { exportSnapshotToGDevelop, type TamaGDevelopExport } from "./gdevelop-state";
import type { TamaSessionState } from "./session";

export interface TamaGDevelopDispatchResponse extends TamaDispatchResponse {
  gdevelop?: TamaGDevelopExport;
}

export function dispatchSessionActionForGDevelop(
  state: TamaDispatchState,
  action: TamaDispatchAction,
): TamaGDevelopDispatchResponse {
  const response = dispatchSessionAction(state, action);

  if (!response.ok) {
    return response;
  }

  return {
    ...response,
    gdevelop: exportSnapshotToGDevelop(response.snapshot),
  };
}

export function createGDevelopState(session?: TamaSessionState): TamaGDevelopExport | undefined {
  if (!session) return undefined;

  return exportSnapshotToGDevelop({
    pet: {
      ...session.pet,
      activeEffects: Array.isArray(session.pet.activeEffects) ? [...session.pet.activeEffects] : [],
    },
    inventory: session.inventory.map((entry) => ({ ...entry })),
    notifications: session.notifications.map((entry) => ({ ...entry })),
    quests: session.quests.map((entry) => ({
      ...entry,
      objectives: entry.objectives.map((objective) => ({ ...objective })),
      progress: entry.progress.map((progress) => ({ ...progress })),
      rewards: entry.rewards.map((reward) => ({ ...reward })),
    })),
    items: session.items.map((entry) => ({
      ...entry,
      changes: Array.isArray(entry.changes) ? entry.changes.map((change) => ({ ...change })) : [],
      timedEffects: Array.isArray(entry.timedEffects)
        ? entry.timedEffects.map((effect) => ({ ...effect }))
        : [],
      tags: Array.isArray(entry.tags) ? [...entry.tags] : [],
    })),
    events: session.events.map((entry) => ({
      ...entry,
      payload:
        entry.payload && typeof entry.payload === "object"
          ? { ...(entry.payload as Record<string, unknown>) }
          : entry.payload,
    })),
    coins: session.coins,
    createdAt: session.createdAt,
    updatedAt: session.updatedAt,
    lastActionAt: session.lastActionAt,
  });
}
