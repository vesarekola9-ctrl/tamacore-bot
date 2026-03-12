export type TamaStatKey =
  | "energy"
  | "hunger"
  | "happiness"
  | "hygiene"
  | "health";

export type TamaEffectOp = "add" | "mul" | "set";

export interface TamaTimedEffect {
  id: string;
  sourceId: string;
  sourceType: "food" | "cosmetic" | "system";
  stat: TamaStatKey;
  op: TamaEffectOp;
  value: number;
  durationMs: number;
  startedAt: number;
  expiresAt: number;
  stackKey?: string;
  maxStacks?: number;
}

export interface TamaPetLike {
  energy?: number;
  hunger?: number;
  happiness?: number;
  hygiene?: number;
  health?: number;
  activeEffects?: TamaTimedEffect[];
  updatedAt?: number;
  [key: string]: unknown;
}

export interface ApplyEffectInput {
  id: string;
  sourceId: string;
  sourceType: "food" | "cosmetic" | "system";
  stat: TamaStatKey;
  op: TamaEffectOp;
  value: number;
  durationMs: number;
  stackKey?: string;
  maxStacks?: number;
  now?: number;
}

const STAT_MIN = 0;
const STAT_MAX = 100;

function clamp(value: number, min = STAT_MIN, max = STAT_MAX): number {
  return Math.max(min, Math.min(max, value));
}

function getNow(now?: number): number {
  return Number.isFinite(now) ? Number(now) : Date.now();
}

function getStat(pet: TamaPetLike, stat: TamaStatKey): number {
  const value = pet[stat];
  return typeof value === "number" && Number.isFinite(value) ? value : 0;
}

function setStat(pet: TamaPetLike, stat: TamaStatKey, value: number): void {
  pet[stat] = clamp(value);
}

function ensureEffects(pet: TamaPetLike): TamaTimedEffect[] {
  if (!Array.isArray(pet.activeEffects)) pet.activeEffects = [];
  return pet.activeEffects;
}

function removeExpiredEffects(
  pet: TamaPetLike,
  now = Date.now(),
): TamaTimedEffect[] {
  const effects = ensureEffects(pet);
  const active = effects.filter((effect) => effect.expiresAt > now);
  pet.activeEffects = active;
  return active;
}

function enforceStacks(
  effects: TamaTimedEffect[],
  nextEffect: TamaTimedEffect,
): TamaTimedEffect[] {
  if (!nextEffect.stackKey || !nextEffect.maxStacks || nextEffect.maxStacks < 1) {
    return [...effects, nextEffect];
  }

  const sameStack = effects
    .filter((e) => e.stackKey === nextEffect.stackKey)
    .sort((a, b) => a.startedAt - b.startedAt);

  const nonStack = effects.filter((e) => e.stackKey !== nextEffect.stackKey);

  const trimmed = [...sameStack, nextEffect].slice(-nextEffect.maxStacks);
  return [...nonStack, ...trimmed];
}

export function applyTimedEffect(
  pet: TamaPetLike,
  input: ApplyEffectInput,
): TamaTimedEffect {
  const now = getNow(input.now);

  removeExpiredEffects(pet, now);

  const effect: TamaTimedEffect = {
    id: input.id,
    sourceId: input.sourceId,
    sourceType: input.sourceType,
    stat: input.stat,
    op: input.op,
    value: input.value,
    durationMs: input.durationMs,
    startedAt: now,
    expiresAt: now + input.durationMs,
    stackKey: input.stackKey,
    maxStacks: input.maxStacks,
  };

  pet.activeEffects = enforceStacks(ensureEffects(pet), effect);
  pet.updatedAt = now;
  return effect;
}

export function tickEffects(
  pet: TamaPetLike,
  now = Date.now(),
): TamaPetLike {
  const activeEffects = removeExpiredEffects(pet, now);

  const next: TamaPetLike = {
    ...pet,
    activeEffects: [...activeEffects],
    updatedAt: now,
  };

  const baseStats: Record<TamaStatKey, number> = {
    energy: getStat(next, "energy"),
    hunger: getStat(next, "hunger"),
    happiness: getStat(next, "happiness"),
    hygiene: getStat(next, "hygiene"),
    health: getStat(next, "health"),
  };

  const statBuckets: Record<TamaStatKey, TamaTimedEffect[]> = {
    energy: [],
    hunger: [],
    happiness: [],
    hygiene: [],
    health: [],
  };

  for (const effect of activeEffects) {
    statBuckets[effect.stat].push(effect);
  }

  (Object.keys(statBuckets) as TamaStatKey[]).forEach((stat) => {
    let value = baseStats[stat];

    for (const effect of statBuckets[stat]) {
      if (effect.op === "set") value = effect.value;
    }

    for (const effect of statBuckets[stat]) {
      if (effect.op === "add") value += effect.value;
    }

    for (const effect of statBuckets[stat]) {
      if (effect.op === "mul") value *= effect.value;
    }

    setStat(next, stat, value);
  });

  return next;
}

export function clearEffectBySource(
  pet: TamaPetLike,
  sourceId: string,
  now = Date.now(),
): TamaPetLike {
  const active = removeExpiredEffects(pet, now).filter(
    (effect) => effect.sourceId !== sourceId,
  );

  return {
    ...pet,
    activeEffects: active,
    updatedAt: now,
  };
}

export function hasActiveEffect(
  pet: TamaPetLike,
  sourceId: string,
  now = Date.now(),
): boolean {
  return removeExpiredEffects(pet, now).some((effect) => effect.sourceId === sourceId);
}
