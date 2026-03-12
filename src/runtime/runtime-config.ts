import type { TamaCatalogItem } from "./catalog";
import type { TamaInventoryEntry } from "./inventory";
import type { TamaPetState } from "./pet-state";
import type { TamaQuestDefinition } from "./quests";
import { validateRuntimeBootstrapConfig, type TamaRuntimeValidationResult } from "./validator";

export interface TamaRuntimeDecayConfig {
  energyPerMinute: number;
  hungerPerMinute: number;
  happinessPerMinute: number;
  hygienePerMinute: number;
}

export interface TamaRuntimeLoopConfig {
  tickIntervalMs: number;
  notificationLimit: number;
  eventQueueLimit: number;
  questAutoClaim: boolean;
}

export interface TamaRuntimeBootstrapConfigFile {
  pet?: Partial<TamaPetState>;
  items?: TamaCatalogItem[];
  quests?: TamaQuestDefinition[];
  inventory?: TamaInventoryEntry[];
  coins?: number;
  decay?: Partial<TamaRuntimeDecayConfig>;
  loop?: Partial<TamaRuntimeLoopConfig>;
}

export interface TamaResolvedRuntimeConfig {
  pet: Partial<TamaPetState>;
  items: TamaCatalogItem[];
  quests: TamaQuestDefinition[];
  inventory: TamaInventoryEntry[];
  coins: number;
  decay: TamaRuntimeDecayConfig;
  loop: TamaRuntimeLoopConfig;
}

export interface TamaResolvedRuntimeConfigResult {
  ok: boolean;
  config: TamaResolvedRuntimeConfig;
  validation: TamaRuntimeValidationResult;
}

const DEFAULT_DECAY: TamaRuntimeDecayConfig = {
  energyPerMinute: 0.35,
  hungerPerMinute: 0.45,
  happinessPerMinute: 0.2,
  hygienePerMinute: 0.25,
};

const DEFAULT_LOOP: TamaRuntimeLoopConfig = {
  tickIntervalMs: 1000,
  notificationLimit: 50,
  eventQueueLimit: 100,
  questAutoClaim: false,
};

function safeNumber(value: unknown, fallback: number): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function safeBoolean(value: unknown, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function clonePet(pet?: Partial<TamaPetState>): Partial<TamaPetState> {
  if (!pet) return {};

  return {
    ...pet,
    activeEffects: Array.isArray(pet.activeEffects) ? [...pet.activeEffects] : [],
  };
}

function cloneInventory(entries?: TamaInventoryEntry[]): TamaInventoryEntry[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({
    itemId: entry.itemId,
    quantity: entry.quantity,
  }));
}

function cloneItems(items?: TamaCatalogItem[]): TamaCatalogItem[] {
  if (!Array.isArray(items)) return [];
  return items.map((item) => ({
    ...item,
    changes: Array.isArray(item.changes) ? item.changes.map((change) => ({ ...change })) : [],
    timedEffects: Array.isArray(item.timedEffects)
      ? item.timedEffects.map((effect) => ({ ...effect }))
      : [],
    tags: Array.isArray(item.tags) ? [...item.tags] : [],
  }));
}

function cloneQuests(quests?: TamaQuestDefinition[]): TamaQuestDefinition[] {
  if (!Array.isArray(quests)) return [];
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

export function resolveRuntimeConfig(
  input?: TamaRuntimeBootstrapConfigFile,
): TamaResolvedRuntimeConfigResult {
  const config: TamaResolvedRuntimeConfig = {
    pet: clonePet(input?.pet),
    items: cloneItems(input?.items),
    quests: cloneQuests(input?.quests),
    inventory: cloneInventory(input?.inventory),
    coins: Math.max(0, Math.floor(safeNumber(input?.coins, 0))),
    decay: {
      energyPerMinute: safeNumber(input?.decay?.energyPerMinute, DEFAULT_DECAY.energyPerMinute),
      hungerPerMinute: safeNumber(input?.decay?.hungerPerMinute, DEFAULT_DECAY.hungerPerMinute),
      happinessPerMinute: safeNumber(
        input?.decay?.happinessPerMinute,
        DEFAULT_DECAY.happinessPerMinute,
      ),
      hygienePerMinute: safeNumber(input?.decay?.hygienePerMinute, DEFAULT_DECAY.hygienePerMinute),
    },
    loop: {
      tickIntervalMs: Math.max(50, Math.floor(safeNumber(input?.loop?.tickIntervalMs, DEFAULT_LOOP.tickIntervalMs))),
      notificationLimit: Math.max(
        1,
        Math.floor(safeNumber(input?.loop?.notificationLimit, DEFAULT_LOOP.notificationLimit)),
      ),
      eventQueueLimit: Math.max(
        1,
        Math.floor(safeNumber(input?.loop?.eventQueueLimit, DEFAULT_LOOP.eventQueueLimit)),
      ),
      questAutoClaim: safeBoolean(input?.loop?.questAutoClaim, DEFAULT_LOOP.questAutoClaim),
    },
  };

  const validation = validateRuntimeBootstrapConfig({
    pet: config.pet,
    items: config.items,
    quests: config.quests,
    inventory: config.inventory,
    coins: config.coins,
  });

  return {
    ok: validation.ok,
    config,
    validation,
  };
}
