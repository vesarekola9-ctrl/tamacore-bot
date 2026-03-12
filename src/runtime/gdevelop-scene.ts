import type { TamaGDevelopArrayItem, TamaGDevelopExport, TamaGDevelopVariableMap } from "./gdevelop-state";
import type { TamaBridgeSnapshot } from "./bridge";

export interface TamaGDevelopSceneVariable {
  name: string;
  value: string | number | boolean;
}

export interface TamaGDevelopSceneArrayRow {
  id?: string;
  index: number;
  values: Record<string, string | number | boolean>;
}

export interface TamaGDevelopSceneState {
  variables: TamaGDevelopSceneVariable[];
  inventory: TamaGDevelopSceneArrayRow[];
  notifications: TamaGDevelopSceneArrayRow[];
  quests: TamaGDevelopSceneArrayRow[];
  catalog: TamaGDevelopSceneArrayRow[];
  events: TamaGDevelopSceneArrayRow[];
}

function mapVariables(input: TamaGDevelopVariableMap): TamaGDevelopSceneVariable[] {
  return Object.keys(input)
    .sort((a, b) => a.localeCompare(b))
    .map((key) => ({
      name: key,
      value: input[key],
    }));
}

function mapRows(input: TamaGDevelopArrayItem[]): TamaGDevelopSceneArrayRow[] {
  const rows = new Map<number, TamaGDevelopSceneArrayRow>();

  for (const item of input) {
    const existing = rows.get(item.index) ?? {
      id: item.id,
      index: item.index,
      values: {},
    };

    if (item.id && !existing.id) existing.id = item.id;
    if (item.key) existing.values[item.key] = item.value;

    rows.set(item.index, existing);
  }

  return Array.from(rows.values()).sort((a, b) => a.index - b.index);
}

export function toGDevelopSceneState(
  input: TamaGDevelopExport,
): TamaGDevelopSceneState {
  return {
    variables: mapVariables(input.variables),
    inventory: mapRows(input.inventory),
    notifications: mapRows(input.notifications),
    quests: mapRows(input.quests),
    catalog: mapRows(input.catalog),
    events: mapRows(input.events),
  };
}

export function getSceneVariableValue(
  state: TamaGDevelopSceneState,
  name: string,
): string | number | boolean | undefined {
  const found = state.variables.find((entry) => entry.name === name);
  return found?.value;
}

export function getSceneRowsByCollection(
  state: TamaGDevelopSceneState,
  collection: "inventory" | "notifications" | "quests" | "catalog" | "events",
): TamaGDevelopSceneArrayRow[] {
  return state[collection].map((row) => ({
    id: row.id,
    index: row.index,
    values: { ...row.values },
  }));
}

export function findSceneRowById(
  rows: TamaGDevelopSceneArrayRow[],
  id: string,
): TamaGDevelopSceneArrayRow | undefined {
  const found = rows.find((row) => row.id === id);
  return found
    ? {
        id: found.id,
        index: found.index,
        values: { ...found.values },
      }
    : undefined;
}

export function createSceneStateFromSnapshotExport(
  snapshotExport: TamaGDevelopExport,
): TamaGDevelopSceneState {
  return toGDevelopSceneState(snapshotExport);
}

export function createMinimalSceneVariableMap(
  snapshot: TamaBridgeSnapshot,
): TamaGDevelopVariableMap {
  return {
    "Pet.Energy": snapshot.pet.energy,
    "Pet.Hunger": snapshot.pet.hunger,
    "Pet.Happiness": snapshot.pet.happiness,
    "Pet.Hygiene": snapshot.pet.hygiene,
    "Pet.Health": snapshot.pet.health,
    "Pet.Mood": snapshot.pet.mood ?? "",
    "Session.Coins": snapshot.coins,
    "Counts.Inventory": snapshot.inventory.length,
    "Counts.Notifications": snapshot.notifications.length,
    "Counts.Quests": snapshot.quests.length,
    "Counts.Events": snapshot.events.length,
  };
}
