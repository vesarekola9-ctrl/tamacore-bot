import type { TamaCatalogItem } from "./catalog";
import type { TamaInventoryEntry } from "./inventory";
import type { TamaNotification } from "./notifications";
import type { TamaPetState } from "./pet-state";
import type { TamaQuestState } from "./quests";
import type { TamaBridgeSnapshot } from "./bridge";
import type { TamaSessionEvent } from "./session-events";

export interface TamaGDevelopVariableMap {
  [key: string]: string | number | boolean;
}

export interface TamaGDevelopArrayItem {
  index: number;
  id?: string;
  key?: string;
  value: string | number | boolean;
}

export interface TamaGDevelopExport {
  variables: TamaGDevelopVariableMap;
  inventory: TamaGDevelopArrayItem[];
  notifications: TamaGDevelopArrayItem[];
  quests: TamaGDevelopArrayItem[];
  catalog: TamaGDevelopArrayItem[];
  events: TamaGDevelopArrayItem[];
}

function safeNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function safeString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function safeBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function encodeTags(tags?: string[]): string {
  return Array.isArray(tags) ? tags.join("|") : "";
}

function pushRow(
  rows: TamaGDevelopArrayItem[],
  index: number,
  key: string,
  value: string | number | boolean,
  id?: string,
): void {
  rows.push({
    index,
    key,
    value,
    id,
  });
}

function exportPetVariables(
  target: TamaGDevelopVariableMap,
  pet: TamaPetState,
): void {
  target["Pet.Energy"] = safeNumber(pet.energy);
  target["Pet.Hunger"] = safeNumber(pet.hunger);
  target["Pet.Happiness"] = safeNumber(pet.happiness);
  target["Pet.Hygiene"] = safeNumber(pet.hygiene);
  target["Pet.Health"] = safeNumber(pet.health);
  target["Pet.IsHungry"] = safeBoolean(pet.isHungry);
  target["Pet.IsTired"] = safeBoolean(pet.isTired);
  target["Pet.IsDirty"] = safeBoolean(pet.isDirty);
  target["Pet.IsSick"] = safeBoolean(pet.isSick);
  target["Pet.Mood"] = safeString(pet.mood);
  target["Pet.CreatedAt"] = safeNumber(pet.createdAt);
  target["Pet.UpdatedAt"] = safeNumber(pet.updatedAt);
  target["Pet.LastTickAt"] = safeNumber(pet.lastTickAt);
  target["Pet.ActiveEffectsCount"] = Array.isArray(pet.activeEffects) ? pet.activeEffects.length : 0;
}

function exportInventoryRows(entries: TamaInventoryEntry[]): TamaGDevelopArrayItem[] {
  const rows: TamaGDevelopArrayItem[] = [];

  entries.forEach((entry, index) => {
    pushRow(rows, index, "itemId", safeString(entry.itemId), entry.itemId);
    pushRow(rows, index, "quantity", safeNumber(entry.quantity), entry.itemId);
  });

  return rows;
}

function exportNotificationRows(entries: TamaNotification[]): TamaGDevelopArrayItem[] {
  const rows: TamaGDevelopArrayItem[] = [];

  entries.forEach((entry, index) => {
    pushRow(rows, index, "id", safeString(entry.id), entry.id);
    pushRow(rows, index, "code", safeString(entry.code), entry.id);
    pushRow(rows, index, "level", safeString(entry.level), entry.id);
    pushRow(rows, index, "message", safeString(entry.message), entry.id);
    pushRow(rows, index, "createdAt", safeNumber(entry.createdAt), entry.id);
    pushRow(rows, index, "read", safeBoolean(entry.read), entry.id);
  });

  return rows;
}

function exportQuestRows(entries: TamaQuestState[]): TamaGDevelopArrayItem[] {
  const rows: TamaGDevelopArrayItem[] = [];

  entries.forEach((entry, index) => {
    pushRow(rows, index, "id", safeString(entry.id), entry.id);
    pushRow(rows, index, "title", safeString(entry.title), entry.id);
    pushRow(rows, index, "description", safeString(entry.description), entry.id);
    pushRow(rows, index, "status", safeString(entry.status), entry.id);
    pushRow(rows, index, "completedAt", safeNumber(entry.completedAt), entry.id);
    pushRow(rows, index, "claimedAt", safeNumber(entry.claimedAt), entry.id);
    pushRow(rows, index, "objectiveCount", entry.objectives.length, entry.id);
    pushRow(
      rows,
      index,
      "completedObjectives",
      entry.progress.filter((item) => item.completed).length,
      entry.id,
    );
    pushRow(rows, index, "rewardCount", entry.rewards.length, entry.id);
  });

  return rows;
}

function exportCatalogRows(entries: TamaCatalogItem[]): TamaGDevelopArrayItem[] {
  const rows: TamaGDevelopArrayItem[] = [];

  entries.forEach((entry, index) => {
    pushRow(rows, index, "id", safeString(entry.id), entry.id);
    pushRow(rows, index, "kind", safeString(entry.kind), entry.id);
    pushRow(rows, index, "name", safeString(entry.name), entry.id);
    pushRow(rows, index, "description", safeString(entry.description), entry.id);
    pushRow(rows, index, "price", safeNumber(entry.price), entry.id);
    pushRow(rows, index, "tags", encodeTags(entry.tags), entry.id);
    pushRow(
      rows,
      index,
      "instantChangeCount",
      Array.isArray(entry.changes) ? entry.changes.length : 0,
      entry.id,
    );
    pushRow(
      rows,
      index,
      "timedEffectCount",
      Array.isArray(entry.timedEffects) ? entry.timedEffects.length : 0,
      entry.id,
    );
  });

  return rows;
}

function exportEventRows(entries: TamaSessionEvent[]): TamaGDevelopArrayItem[] {
  const rows: TamaGDevelopArrayItem[] = [];

  entries.forEach((entry, index) => {
    pushRow(rows, index, "id", safeString(entry.id), entry.id);
    pushRow(rows, index, "type", safeString(entry.type), entry.id);
    pushRow(rows, index, "createdAt", safeNumber(entry.createdAt), entry.id);
    pushRow(
      rows,
      index,
      "payload",
      JSON.stringify(entry.payload ?? {}),
      entry.id,
    );
  });

  return rows;
}

export function exportSnapshotToGDevelop(
  snapshot: TamaBridgeSnapshot,
): TamaGDevelopExport {
  const variables: TamaGDevelopVariableMap = {};

  exportPetVariables(variables, snapshot.pet);

  variables["Session.Coins"] = safeNumber(snapshot.coins);
  variables["Session.CreatedAt"] = safeNumber(snapshot.createdAt);
  variables["Session.UpdatedAt"] = safeNumber(snapshot.updatedAt);
  variables["Session.LastActionAt"] = safeNumber(snapshot.lastActionAt);

  variables["Counts.Inventory"] = snapshot.inventory.length;
  variables["Counts.Notifications"] = snapshot.notifications.length;
  variables["Counts.NotificationsUnread"] = snapshot.notifications.filter((item) => !item.read).length;
  variables["Counts.Quests"] = snapshot.quests.length;
  variables["Counts.QuestsCompleted"] = snapshot.quests.filter((item) => item.status === "completed").length;
  variables["Counts.QuestsClaimed"] = snapshot.quests.filter((item) => item.status === "claimed").length;
  variables["Counts.Catalog"] = snapshot.items.length;
  variables["Counts.Events"] = snapshot.events.length;

  return {
    variables,
    inventory: exportInventoryRows(snapshot.inventory),
    notifications: exportNotificationRows(snapshot.notifications),
    quests: exportQuestRows(snapshot.quests),
    catalog: exportCatalogRows(snapshot.items),
    events: exportEventRows(snapshot.events),
  };
}
