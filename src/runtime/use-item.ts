import { applyTimedEffect, type TamaEffectOp, type TamaPetLike, type TamaStatKey } from "./effects";

export type TamaItemKind = "food" | "cosmetic";

export interface TamaInstantStatChange {
  stat: TamaStatKey;
  amount: number;
}

export interface TamaTimedStatChange {
  stat: TamaStatKey;
  op: TamaEffectOp;
  value: number;
  durationMs: number;
  stackKey?: string;
  maxStacks?: number;
}

export interface TamaUsableItem {
  id: string;
  kind: TamaItemKind;
  changes?: TamaInstantStatChange[];
  timedEffects?: TamaTimedStatChange[];
}

export interface UseItemResult {
  pet: TamaPetLike;
  consumed: boolean;
  usedItemId: string;
  usedItemKind: TamaItemKind;
  appliedInstantChanges: TamaInstantStatChange[];
  appliedTimedEffects: string[];
}

const STAT_MIN = 0;
const STAT_MAX = 100;

function clamp(value: number, min = STAT_MIN, max = STAT_MAX): number {
  return Math.max(min, Math.min(max, value));
}

function readStat(pet: TamaPetLike, stat: TamaStatKey): number {
  const value = pet[stat];
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function writeStat(pet: TamaPetLike, stat: TamaStatKey, value: number): void {
  pet[stat] = clamp(value);
}

function applyInstantChanges(
  pet: TamaPetLike,
  changes: TamaInstantStatChange[],
): TamaInstantStatChange[] {
  const applied: TamaInstantStatChange[] = [];

  for (const change of changes) {
    const current = readStat(pet, change.stat);
    writeStat(pet, change.stat, current + change.amount);
    applied.push(change);
  }

  return applied;
}

function normalizeChanges(changes?: TamaInstantStatChange[]): TamaInstantStatChange[] {
  if (!Array.isArray(changes)) return [];
  return changes.filter(
    (change) =>
      !!change &&
      typeof change.stat === "string" &&
      typeof change.amount === "number" &&
      Number.isFinite(change.amount),
  );
}

function normalizeTimedEffects(effects?: TamaTimedStatChange[]): TamaTimedStatChange[] {
  if (!Array.isArray(effects)) return [];
  return effects.filter(
    (effect) =>
      !!effect &&
      typeof effect.stat === "string" &&
      typeof effect.op === "string" &&
      typeof effect.value === "number" &&
      Number.isFinite(effect.value) &&
      typeof effect.durationMs === "number" &&
      Number.isFinite(effect.durationMs) &&
      effect.durationMs > 0,
  );
}

export function useItem(
  pet: TamaPetLike,
  item: TamaUsableItem,
  now = Date.now(),
): UseItemResult {
  const nextPet: TamaPetLike = {
    ...pet,
    activeEffects: Array.isArray(pet.activeEffects) ? [...pet.activeEffects] : [],
    updatedAt: now,
  };

  const instantChanges = normalizeChanges(item.changes);
  const timedEffects = normalizeTimedEffects(item.timedEffects);

  const appliedInstantChanges = applyInstantChanges(nextPet, instantChanges);
  const appliedTimedEffects: string[] = [];

  for (let i = 0; i < timedEffects.length; i += 1) {
    const effect = timedEffects[i];
    const effectId = `${item.kind}:${item.id}:fx:${i}:${now}`;

    applyTimedEffect(nextPet, {
      id: effectId,
      sourceId: item.id,
      sourceType: item.kind,
      stat: effect.stat,
      op: effect.op,
      value: effect.value,
      durationMs: effect.durationMs,
      stackKey: effect.stackKey,
      maxStacks: effect.maxStacks,
      now,
    });

    appliedTimedEffects.push(effectId);
  }

  nextPet.updatedAt = now;

  return {
    pet: nextPet,
    consumed: appliedInstantChanges.length > 0 || appliedTimedEffects.length > 0,
    usedItemId: item.id,
    usedItemKind: item.kind,
    appliedInstantChanges,
    appliedTimedEffects,
  };
}
