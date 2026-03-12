import {
  dispatchFullLoopAction,
  type TamaFullLoopActionResult,
  type TamaFullLoopState,
} from "./full-loop-controller";
import type { TamaAnyLiveLoopAction } from "./gdevelop-live-loop";

export type TamaAiDecisionReason =
  | "HUNGER_CRITICAL"
  | "ENERGY_CRITICAL"
  | "HYGIENE_CRITICAL"
  | "HAPPINESS_CRITICAL"
  | "HEALTH_CRITICAL"
  | "LOW_HUNGER"
  | "LOW_ENERGY"
  | "LOW_HYGIENE"
  | "LOW_HAPPINESS"
  | "WORLD_NIGHT"
  | "IDLE";

export interface TamaAiDecision {
  action: TamaAnyLiveLoopAction | null;
  reason: TamaAiDecisionReason;
  score: number;
}

export interface TamaAiControllerConfig {
  hungerCritical: number;
  energyCritical: number;
  hygieneCritical: number;
  happinessCritical: number;
  healthCritical: number;
  hungerLow: number;
  energyLow: number;
  hygieneLow: number;
  happinessLow: number;
  enabled: boolean;
}

export interface TamaAiControllerState {
  config: TamaAiControllerConfig;
  lastDecisionAt: number;
  decisionCount: number;
}

export interface TamaAiStepResult {
  loop: TamaFullLoopState;
  ai: TamaAiControllerState;
  decision: TamaAiDecision;
  result?: TamaFullLoopActionResult;
}

export function createAiControllerConfig(): TamaAiControllerConfig {
  return {
    hungerCritical: 85,
    energyCritical: 20,
    hygieneCritical: 25,
    happinessCritical: 25,
    healthCritical: 30,
    hungerLow: 65,
    energyLow: 35,
    hygieneLow: 40,
    happinessLow: 40,
    enabled: true,
  };
}

export function createAiControllerState(
  config?: Partial<TamaAiControllerConfig>,
): TamaAiControllerState {
  return {
    config: {
      ...createAiControllerConfig(),
      ...(config ?? {}),
    },
    lastDecisionAt: 0,
    decisionCount: 0,
  };
}

function clampNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function getStat(loop: TamaFullLoopState, key: "energy" | "hunger" | "hygiene" | "happiness" | "health"): number {
  return clampNumber(loop.ui.stats[key], 0);
}

function getWorldFlag(loop: TamaFullLoopState, key: "isNight" | "isMorning" | "isEvening"): boolean {
  return !!loop.ui.world[key];
}

function tryAction(type: TamaAnyLiveLoopAction["type"], itemId: string): TamaAnyLiveLoopAction {
  return {
    type,
    payload: {
      itemId,
      now: Date.now(),
    },
  } as TamaAnyLiveLoopAction;
}

function buildFeedAction(): TamaAnyLiveLoopAction {
  return tryAction("USE_ITEM", "food");
}

function buildSleepAction(): TamaAnyLiveLoopAction {
  return {
    type: "WORLD_SET_ZONE",
    payload: {
      zone: "sleep",
    },
  };
}

function buildCleanAction(): TamaAnyLiveLoopAction {
  return tryAction("USE_ITEM", "soap");
}

function buildPlayAction(): TamaAnyLiveLoopAction {
  return tryAction("USE_ITEM", "toy");
}

function buildHealAction(): TamaAnyLiveLoopAction {
  return tryAction("USE_ITEM", "medicine");
}

export function decideAiAction(
  loop: TamaFullLoopState,
  ai: TamaAiControllerState,
): TamaAiDecision {
  if (!ai.config.enabled) {
    return {
      action: null,
      reason: "IDLE",
      score: 0,
    };
  }

  const hunger = getStat(loop, "hunger");
  const energy = getStat(loop, "energy");
  const hygiene = getStat(loop, "hygiene");
  const happiness = getStat(loop, "happiness");
  const health = getStat(loop, "health");
  const isNight = getWorldFlag(loop, "isNight");

  if (health <= ai.config.healthCritical) {
    return {
      action: buildHealAction(),
      reason: "HEALTH_CRITICAL",
      score: 100,
    };
  }

  if (hunger >= ai.config.hungerCritical) {
    return {
      action: buildFeedAction(),
      reason: "HUNGER_CRITICAL",
      score: 95,
    };
  }

  if (energy <= ai.config.energyCritical) {
    return {
      action: buildSleepAction(),
      reason: "ENERGY_CRITICAL",
      score: 90,
    };
  }

  if (hygiene <= ai.config.hygieneCritical) {
    return {
      action: buildCleanAction(),
      reason: "HYGIENE_CRITICAL",
      score: 85,
    };
  }

  if (happiness <= ai.config.happinessCritical) {
    return {
      action: buildPlayAction(),
      reason: "HAPPINESS_CRITICAL",
      score: 80,
    };
  }

  if (hunger >= ai.config.hungerLow) {
    return {
      action: buildFeedAction(),
      reason: "LOW_HUNGER",
      score: 60,
    };
  }

  if (energy <= ai.config.energyLow || isNight) {
    return {
      action: buildSleepAction(),
      reason: isNight ? "WORLD_NIGHT" : "LOW_ENERGY",
      score: 55,
    };
  }

  if (hygiene <= ai.config.hygieneLow) {
    return {
      action: buildCleanAction(),
      reason: "LOW_HYGIENE",
      score: 50,
    };
  }

  if (happiness <= ai.config.happinessLow) {
    return {
      action: buildPlayAction(),
      reason: "LOW_HAPPINESS",
      score: 45,
    };
  }

  return {
    action: null,
    reason: "IDLE",
    score: 0,
  };
}

export function runAiStep(
  loop: TamaFullLoopState,
  ai: TamaAiControllerState,
  now = Date.now(),
): TamaAiStepResult {
  const decision = decideAiAction(loop, ai);

  const nextAi: TamaAiControllerState = {
    config: {
      ...ai.config,
    },
    lastDecisionAt: now,
    decisionCount: ai.decisionCount + 1,
  };

  if (!decision.action) {
    return {
      loop,
      ai: nextAi,
      decision,
    };
  }

  const result = dispatchFullLoopAction(loop, decision.action);

  return {
    loop: result.state,
    ai: nextAi,
    decision,
    result,
  };
}
