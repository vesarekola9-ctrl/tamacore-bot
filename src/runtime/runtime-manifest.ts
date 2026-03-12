import type { TamaCatalogItem } from "./catalog";
import type { TamaInventoryEntry } from "./inventory";
import type { TamaPetState } from "./pet-state";
import type { TamaQuestDefinition } from "./quests";
import {
  resolveRuntimeConfig,
  type TamaResolvedRuntimeConfig,
  type TamaRuntimeBootstrapConfigFile,
} from "./runtime-config";
import type { TamaRuntimeValidationIssue } from "./validator";

export interface TamaRuntimeManifest {
  version: "1.0";
  generatedAt: number;
  valid: boolean;
  issues: TamaRuntimeValidationIssue[];
  config: {
    pet: Partial<TamaPetState>;
    inventory: TamaInventoryEntry[];
    items: TamaCatalogItem[];
    quests: TamaQuestDefinition[];
    coins: number;
    decay: TamaResolvedRuntimeConfig["decay"];
    loop: TamaResolvedRuntimeConfig["loop"];
  };
  counts: {
    inventory: number;
    items: number;
    quests: number;
  };
}

function clonePet(pet: Partial<TamaPetState>): Partial<TamaPetState> {
  return {
    ...pet,
    activeEffects: Array.isArray(pet.activeEffects) ? [...pet.activeEffects] : [],
  };
}

function cloneInventory(entries: TamaInventoryEntry[]): TamaInventoryEntry[] {
  return entries.map((entry) => ({
    itemId: entry.itemId,
    quantity: entry.quantity,
  }));
}

function cloneItems(items: TamaCatalogItem[]): TamaCatalogItem[] {
  return items.map((item) => ({
    ...item,
    changes: Array.isArray(item.changes) ? item.changes.map((change) => ({ ...change })) : [],
    timedEffects: Array.isArray(item.timedEffects)
      ? item.timedEffects.map((effect) => ({ ...effect }))
      : [],
    tags: Array.isArray(item.tags) ? [...item.tags] : [],
  }));
}

function cloneQuests(quests: TamaQuestDefinition[]): TamaQuestDefinition[] {
  return quests.map((quest) => ({
    ...quest,
    objectives: Array.isArray(quest.objectives)
      ? quest.objectives.map((objective) => ({ ...objective }))
      : [],
    rewards: Array.isArray(quest.rewards)
      ? quest.rewards.map((reward) => ({ ...reward }))
      : [],
  }));
}

export function createRuntimeManifest(
  input?: TamaRuntimeBootstrapConfigFile,
  now = Date.now(),
): TamaRuntimeManifest {
  const resolved = resolveRuntimeConfig(input);

  return {
    version: "1.0",
    generatedAt: now,
    valid: resolved.ok,
    issues: resolved.validation.issues.map((issue) => ({ ...issue })),
    config: {
      pet: clonePet(resolved.config.pet),
      inventory: cloneInventory(resolved.config.inventory),
      items: cloneItems(resolved.config.items),
      quests: cloneQuests(resolved.config.quests),
      coins: resolved.config.coins,
      decay: { ...resolved.config.decay },
      loop: { ...resolved.config.loop },
    },
    counts: {
      inventory: resolved.config.inventory.length,
      items: resolved.config.items.length,
      quests: resolved.config.quests.length,
    },
  };
}

export function serializeRuntimeManifest(
  input?: TamaRuntimeBootstrapConfigFile,
  now = Date.now(),
): string {
  return JSON.stringify(createRuntimeManifest(input, now), null, 2);
}
