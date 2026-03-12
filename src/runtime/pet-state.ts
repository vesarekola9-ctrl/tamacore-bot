import { tickEffects, type TamaPetLike } from "./effects";

export type TamaNeedKey =
  | "energy"
  | "hunger"
  | "happiness"
  | "hygiene"
  | "health";

export interface TamaNeedDecayRates {
  energyPerMinute: number;
  hungerPerMinute: number;
  happinessPerMinute: number;
  hygienePerMinute: number;
}

export interface TamaPetState extends TamaPetLike {
  energy: number;
  hunger: number;
  happiness: number;
  hygiene: number;
  health: number;
  isSick?: boolean;
  isDirty?: boolean;
  isHungry?: boolean;
  isTired?: boolean;
  mood?: string;
  createdAt?: number;
  updatedAt?: number;
  lastTickAt?: number;
}

export interface TamaTickResult {
  pet: TamaPetState;
  elapsedMs: number;
  elapsedMinutes: number;
  changedNeeds: TamaNeedKey[];
}

const STAT_MIN = 0;
const STAT_MAX = 100;

const DEFAULT_DECAY_RATES: TamaNeedDecayRates = {
  energyPerMinute: 0.35,
  hungerPerMinute: 0.45,
  happinessPerMinute: 0.2,
  hygienePerMinute: 0.25,
};

function clamp(value: number, min = STAT_MIN, max = STAT_MAX): number {
  return Math.max(min, Math.min(max, value));
}

function finiteOr(value: unknown, fallback: number): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function readNeed(pet: Partial<TamaPetState>, key: TamaNeedKey, fallback = 100): number {
  return clamp(finiteOr(pet[key], fallback));
}

function setNeed(pet: TamaPetState, key: TamaNeedKey, value: number): void {
  pet[key] = clamp(value);
}

function normalizeDecayRates(
  input?: Partial<TamaNeedDecayRates>,
): TamaNeedDecayRates {
  return {
    energyPerMinute: finiteOr(input?.energyPerMinute, DEFAULT_DECAY_RATES.energyPerMinute),
    hungerPerMinute: finiteOr(input?.hungerPerMinute, DEFAULT_DECAY_RATES.hungerPerMinute),
    happinessPerMinute: finiteOr(
      input?.happinessPerMinute,
      DEFAULT_DECAY_RATES.happinessPerMinute,
    ),
    hygienePerMinute: finiteOr(input?.hygienePerMinute, DEFAULT_DECAY_RATES.hygienePerMinute),
  };
}

function deriveFlags(pet: TamaPetState): void {
  pet.isHungry = pet.hunger <= 30;
  pet.isTired = pet.energy <= 30;
  pet.isDirty = pet.hygiene <= 30;
  pet.isSick = pet.health <= 35;
}

function deriveMood(pet: TamaPetState): void {
  const average =
    (pet.energy + pet.hunger + pet.happiness + pet.hygiene + pet.health) / 5;

  if (pet.health <= 20) {
    pet.mood = "critical";
    return;
  }

  if (pet.isHungry || pet.isTired || pet.isDirty) {
    pet.mood = "needs-care";
    return;
  }

  if (average >= 85) {
    pet.mood = "great";
    return;
  }

  if (average >= 65) {
    pet.mood = "good";
    return;
  }

  if (average >= 40) {
    pet.mood = "okay";
    return;
  }

  pet.mood = "bad";
}

function applyHealthRules(pet: TamaPetState, elapsedMinutes: number): void {
  let healthDelta = 0;

  if (pet.hunger <= 10) healthDelta -= 0.6 * elapsedMinutes;
  else if (pet.hunger <= 25) healthDelta -= 0.25 * elapsedMinutes;

  if (pet.energy <= 10) healthDelta -= 0.45 * elapsedMinutes;
  else if (pet.energy <= 25) healthDelta -= 0.2 * elapsedMinutes;

  if (pet.hygiene <= 10) healthDelta -= 0.5 * elapsedMinutes;
  else if (pet.hygiene <= 25) healthDelta -= 0.2 * elapsedMinutes;

  if (pet.happiness <= 15) healthDelta -= 0.15 * elapsedMinutes;

  if (
    pet.hunger >= 70 &&
    pet.energy >= 70 &&
    pet.hygiene >= 70 &&
    pet.happiness >= 70
  ) {
    healthDelta += 0.12 * elapsedMinutes;
  }

  setNeed(pet, "health", pet.health + healthDelta);
}

export function createPetState(
  initial?: Partial<TamaPetState>,
  now = Date.now(),
): TamaPetState {
  const pet: TamaPetState = {
    energy: readNeed(initial, "energy", 100),
    hunger: readNeed(initial, "hunger", 100),
    happiness: readNeed(initial, "happiness", 100),
    hygiene: readNeed(initial, "hygiene", 100),
    health: readNeed(initial, "health", 100),
    activeEffects: Array.isArray(initial?.activeEffects) ? [...initial.activeEffects] : [],
    createdAt: finiteOr(initial?.createdAt, now),
    updatedAt: now,
    lastTickAt: finiteOr(initial?.lastTickAt, now),
    isSick: Boolean(initial?.isSick),
    isDirty: Boolean(initial?.isDirty),
    isHungry: Boolean(initial?.isHungry),
    isTired: Boolean(initial?.isTired),
    mood: typeof initial?.mood === "string" ? initial.mood : "good",
  };

  deriveFlags(pet);
  deriveMood(pet);
  return pet;
}

export function tickPetState(
  petInput: TamaPetState,
  now = Date.now(),
  decayRates?: Partial<TamaNeedDecayRates>,
): TamaTickResult {
  const pet = createPetState(petInput, finiteOr(petInput.updatedAt, now));
  const rates = normalizeDecayRates(decayRates);
  const lastTickAt = finiteOr(petInput.lastTickAt, now);
  const elapsedMs = Math.max(0, now - lastTickAt);
  const elapsedMinutes = elapsedMs / 60000;

  const before = {
    energy: pet.energy,
    hunger: pet.hunger,
    happiness: pet.happiness,
    hygiene: pet.hygiene,
    health: pet.health,
  };

  setNeed(pet, "energy", pet.energy - rates.energyPerMinute * elapsedMinutes);
  setNeed(pet, "hunger", pet.hunger - rates.hungerPerMinute * elapsedMinutes);
  setNeed(
    pet,
    "happiness",
    pet.happiness - rates.happinessPerMinute * elapsedMinutes,
  );
  setNeed(pet, "hygiene", pet.hygiene - rates.hygienePerMinute * elapsedMinutes);

  applyHealthRules(pet, elapsedMinutes);

  const withEffects = tickEffects(pet, now) as TamaPetState;
  const nextPet = createPetState(
    {
      ...pet,
      ...withEffects,
      createdAt: pet.createdAt,
      lastTickAt: now,
      updatedAt: now,
    },
    now,
  );

  const changedNeeds = (Object.keys(before) as TamaNeedKey[]).filter(
    (key) => Math.abs(before[key] - nextPet[key]) > 0.0001,
  );

  return {
    pet: nextPet,
    elapsedMs,
    elapsedMinutes,
    changedNeeds,
  };
}

export function patchPetNeed(
  petInput: TamaPetState,
  key: TamaNeedKey,
  amount: number,
  now = Date.now(),
): TamaPetState {
  const pet = createPetState(petInput, now);
  setNeed(pet, key, pet[key] + amount);
  pet.updatedAt = now;
  deriveFlags(pet);
  deriveMood(pet);
  return pet;
}
