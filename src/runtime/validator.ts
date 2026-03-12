import type { TamaCatalogItem } from "./catalog";
import type { TamaInventoryEntry } from "./inventory";
import type { TamaPetState } from "./pet-state";
import type { TamaQuestDefinition, TamaQuestObjectiveType } from "./quests";

export interface TamaRuntimeValidationIssue {
  path: string;
  code:
    | "REQUIRED"
    | "TYPE"
    | "RANGE"
    | "DUPLICATE"
    | "UNKNOWN_REF"
    | "INVALID_VALUE";
  message: string;
}

export interface TamaRuntimeValidationResult {
  ok: boolean;
  issues: TamaRuntimeValidationIssue[];
}

export interface TamaRuntimeBootstrapConfig {
  pet?: Partial<TamaPetState>;
  items?: TamaCatalogItem[];
  quests?: TamaQuestDefinition[];
  inventory?: TamaInventoryEntry[];
  coins?: number;
}

const PET_STATS = ["energy", "hunger", "happiness", "hygiene", "health"] as const;
const ITEM_KINDS = new Set(["food", "cosmetic"]);
const EFFECT_OPS = new Set(["add", "mul", "set"]);
const QUEST_OBJECTIVE_TYPES = new Set<TamaQuestObjectiveType>([
  "use-item",
  "gain-item",
  "tick-session",
  "read-notification",
  "pet-mood",
  "pet-stat-at-least",
]);

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function pushIssue(
  issues: TamaRuntimeValidationIssue[],
  path: string,
  code: TamaRuntimeValidationIssue["code"],
  message: string,
): void {
  issues.push({ path, code, message });
}

function validatePet(
  pet: Partial<TamaPetState> | undefined,
  issues: TamaRuntimeValidationIssue[],
): void {
  if (!pet) return;

  for (const stat of PET_STATS) {
    const value = pet[stat];
    if (value === undefined) continue;

    if (!isFiniteNumber(value)) {
      pushIssue(issues, `pet.${stat}`, "TYPE", "Must be a finite number.");
      continue;
    }

    if (value < 0 || value > 100) {
      pushIssue(issues, `pet.${stat}`, "RANGE", "Must be between 0 and 100.");
    }
  }

  if (pet.mood !== undefined && !isNonEmptyString(pet.mood)) {
    pushIssue(issues, "pet.mood", "TYPE", "Must be a non-empty string.");
  }
}

function validateItems(
  items: TamaCatalogItem[] | undefined,
  issues: TamaRuntimeValidationIssue[],
): Set<string> {
  const itemIds = new Set<string>();
  if (!Array.isArray(items)) return itemIds;

  items.forEach((item, index) => {
    const base = `items[${index}]`;

    if (!isNonEmptyString(item?.id)) {
      pushIssue(issues, `${base}.id`, "REQUIRED", "Item id is required.");
    } else {
      if (itemIds.has(item.id)) {
        pushIssue(issues, `${base}.id`, "DUPLICATE", "Duplicate item id.");
      }
      itemIds.add(item.id);
    }

    if (!ITEM_KINDS.has(item?.kind as string)) {
      pushIssue(issues, `${base}.kind`, "INVALID_VALUE", "Item kind must be food or cosmetic.");
    }

    if (item.price !== undefined) {
      if (!isFiniteNumber(item.price)) {
        pushIssue(issues, `${base}.price`, "TYPE", "Price must be a finite number.");
      } else if (item.price < 0) {
        pushIssue(issues, `${base}.price`, "RANGE", "Price must be 0 or more.");
      }
    }

    if (item.changes !== undefined) {
      if (!Array.isArray(item.changes)) {
        pushIssue(issues, `${base}.changes`, "TYPE", "Changes must be an array.");
      } else {
        item.changes.forEach((change, changeIndex) => {
          const changeBase = `${base}.changes[${changeIndex}]`;

          if (!PET_STATS.includes(change?.stat as (typeof PET_STATS)[number])) {
            pushIssue(issues, `${changeBase}.stat`, "INVALID_VALUE", "Unknown stat.");
          }

          if (!isFiniteNumber(change?.amount)) {
            pushIssue(issues, `${changeBase}.amount`, "TYPE", "Amount must be a finite number.");
          }
        });
      }
    }

    if (item.timedEffects !== undefined) {
      if (!Array.isArray(item.timedEffects)) {
        pushIssue(issues, `${base}.timedEffects`, "TYPE", "Timed effects must be an array.");
      } else {
        item.timedEffects.forEach((effect, effectIndex) => {
          const effectBase = `${base}.timedEffects[${effectIndex}]`;

          if (!PET_STATS.includes(effect?.stat as (typeof PET_STATS)[number])) {
            pushIssue(issues, `${effectBase}.stat`, "INVALID_VALUE", "Unknown stat.");
          }

          if (!EFFECT_OPS.has(effect?.op as string)) {
            pushIssue(issues, `${effectBase}.op`, "INVALID_VALUE", "Effect op must be add, mul or set.");
          }

          if (!isFiniteNumber(effect?.value)) {
            pushIssue(issues, `${effectBase}.value`, "TYPE", "Effect value must be a finite number.");
          }

          if (!isFiniteNumber(effect?.durationMs)) {
            pushIssue(issues, `${effectBase}.durationMs`, "TYPE", "durationMs must be a finite number.");
          } else if (effect.durationMs <= 0) {
            pushIssue(issues, `${effectBase}.durationMs`, "RANGE", "durationMs must be greater than 0.");
          }

          if (effect.maxStacks !== undefined) {
            if (!isFiniteNumber(effect.maxStacks)) {
              pushIssue(issues, `${effectBase}.maxStacks`, "TYPE", "maxStacks must be a finite number.");
            } else if (effect.maxStacks < 1) {
              pushIssue(issues, `${effectBase}.maxStacks`, "RANGE", "maxStacks must be at least 1.");
            }
          }
        });
      }
    }
  });

  return itemIds;
}

function validateInventory(
  inventory: TamaInventoryEntry[] | undefined,
  itemIds: Set<string>,
  issues: TamaRuntimeValidationIssue[],
): void {
  if (!Array.isArray(inventory)) return;

  inventory.forEach((entry, index) => {
    const base = `inventory[${index}]`;

    if (!isNonEmptyString(entry?.itemId)) {
      pushIssue(issues, `${base}.itemId`, "REQUIRED", "Inventory itemId is required.");
    } else if (itemIds.size > 0 && !itemIds.has(entry.itemId)) {
      pushIssue(issues, `${base}.itemId`, "UNKNOWN_REF", "Inventory itemId not found in catalog.");
    }

    if (!isFiniteNumber(entry?.quantity)) {
      pushIssue(issues, `${base}.quantity`, "TYPE", "Quantity must be a finite number.");
    } else if (entry.quantity < 0) {
      pushIssue(issues, `${base}.quantity`, "RANGE", "Quantity must be 0 or more.");
    }
  });
}

function validateQuests(
  quests: TamaQuestDefinition[] | undefined,
  itemIds: Set<string>,
  issues: TamaRuntimeValidationIssue[],
): void {
  if (!Array.isArray(quests)) return;

  const questIds = new Set<string>();

  quests.forEach((quest, index) => {
    const base = `quests[${index}]`;

    if (!isNonEmptyString(quest?.id)) {
      pushIssue(issues, `${base}.id`, "REQUIRED", "Quest id is required.");
    } else {
      if (questIds.has(quest.id)) {
        pushIssue(issues, `${base}.id`, "DUPLICATE", "Duplicate quest id.");
      }
      questIds.add(quest.id);
    }

    if (!isNonEmptyString(quest?.title)) {
      pushIssue(issues, `${base}.title`, "REQUIRED", "Quest title is required.");
    }

    if (!Array.isArray(quest?.objectives) || quest.objectives.length === 0) {
      pushIssue(issues, `${base}.objectives`, "REQUIRED", "Quest must have at least one objective.");
    } else {
      const objectiveIds = new Set<string>();

      quest.objectives.forEach((objective, objectiveIndex) => {
        const objectiveBase = `${base}.objectives[${objectiveIndex}]`;

        if (!isNonEmptyString(objective?.id)) {
          pushIssue(issues, `${objectiveBase}.id`, "REQUIRED", "Objective id is required.");
        } else {
          if (objectiveIds.has(objective.id)) {
            pushIssue(issues, `${objectiveBase}.id`, "DUPLICATE", "Duplicate objective id in quest.");
          }
          objectiveIds.add(objective.id);
        }

        if (!QUEST_OBJECTIVE_TYPES.has(objective?.type as TamaQuestObjectiveType)) {
          pushIssue(issues, `${objectiveBase}.type`, "INVALID_VALUE", "Unknown quest objective type.");
        }

        if (objective.stat !== undefined && !PET_STATS.includes(objective.stat)) {
          pushIssue(issues, `${objectiveBase}.stat`, "INVALID_VALUE", "Unknown pet stat.");
        }

        if (objective.required !== undefined) {
          if (!isFiniteNumber(objective.required)) {
            pushIssue(issues, `${objectiveBase}.required`, "TYPE", "required must be a finite number.");
          } else if (objective.required < 1) {
            pushIssue(issues, `${objectiveBase}.required`, "RANGE", "required must be at least 1.");
          }
        }

        if (objective.value !== undefined && !isFiniteNumber(objective.value)) {
          pushIssue(issues, `${objectiveBase}.value`, "TYPE", "value must be a finite number.");
        }

        if (
          (objective.type === "use-item" || objective.type === "gain-item") &&
          !isNonEmptyString(objective.target)
        ) {
          pushIssue(issues, `${objectiveBase}.target`, "REQUIRED", "Objective target item id is required.");
        }

        if (
          (objective.type === "use-item" || objective.type === "gain-item") &&
          isNonEmptyString(objective.target) &&
          itemIds.size > 0 &&
          !itemIds.has(objective.target)
        ) {
          pushIssue(issues, `${objectiveBase}.target`, "UNKNOWN_REF", "Objective target item not found in catalog.");
        }

        if (objective.type === "pet-mood" && !isNonEmptyString(objective.target)) {
          pushIssue(issues, `${objectiveBase}.target`, "REQUIRED", "Mood target is required.");
        }

        if (objective.type === "pet-stat-at-least") {
          if (!objective.stat) {
            pushIssue(issues, `${objectiveBase}.stat`, "REQUIRED", "stat is required.");
          }
          if (!isFiniteNumber(objective.value)) {
            pushIssue(issues, `${objectiveBase}.value`, "REQUIRED", "value is required and must be finite.");
          }
        }
      });
    }

    if (Array.isArray(quest.rewards)) {
      quest.rewards.forEach((reward, rewardIndex) => {
        const rewardBase = `${base}.rewards[${rewardIndex}]`;

        if (!isNonEmptyString(reward?.itemId)) {
          pushIssue(issues, `${rewardBase}.itemId`, "REQUIRED", "Reward itemId is required.");
        } else if (itemIds.size > 0 && !itemIds.has(reward.itemId)) {
          pushIssue(issues, `${rewardBase}.itemId`, "UNKNOWN_REF", "Reward itemId not found in catalog.");
        }

        if (!isFiniteNumber(reward?.quantity)) {
          pushIssue(issues, `${rewardBase}.quantity`, "TYPE", "Reward quantity must be a finite number.");
        } else if (reward.quantity < 1) {
          pushIssue(issues, `${rewardBase}.quantity`, "RANGE", "Reward quantity must be at least 1.");
        }
      });
    }
  });

  quests.forEach((quest, index) => {
    if (
      quest.unlocksOnClaimQuestId !== undefined &&
      !questIds.has(quest.unlocksOnClaimQuestId)
    ) {
      pushIssue(
        issues,
        `quests[${index}].unlocksOnClaimQuestId`,
        "UNKNOWN_REF",
        "Unlock quest id not found.",
      );
    }
  });
}

export function validateRuntimeBootstrapConfig(
  config: TamaRuntimeBootstrapConfig,
): TamaRuntimeValidationResult {
  const issues: TamaRuntimeValidationIssue[] = [];

  if (config.coins !== undefined) {
    if (!isFiniteNumber(config.coins)) {
      pushIssue(issues, "coins", "TYPE", "Coins must be a finite number.");
    } else if (config.coins < 0) {
      pushIssue(issues, "coins", "RANGE", "Coins must be 0 or more.");
    }
  }

  validatePet(config.pet, issues);
  const itemIds = validateItems(config.items, issues);
  validateInventory(config.inventory, itemIds, issues);
  validateQuests(config.quests, itemIds, issues);

  return {
    ok: issues.length === 0,
    issues,
  };
}
