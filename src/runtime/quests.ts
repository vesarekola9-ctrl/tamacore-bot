export type TamaQuestStatus = "locked" | "active" | "completed" | "claimed";

export type TamaQuestObjectiveType =
  | "use-item"
  | "gain-item"
  | "tick-session"
  | "read-notification"
  | "pet-mood"
  | "pet-stat-at-least";

export interface TamaQuestObjective {
  id: string;
  type: TamaQuestObjectiveType;
  target?: string;
  stat?: "energy" | "hunger" | "happiness" | "hygiene" | "health";
  value?: number;
  required?: number;
}

export interface TamaQuestReward {
  itemId: string;
  quantity: number;
}

export interface TamaQuestDefinition {
  id: string;
  title: string;
  description?: string;
  status?: TamaQuestStatus;
  objectives: TamaQuestObjective[];
  rewards?: TamaQuestReward[];
  unlocksOnClaimQuestId?: string;
}

export interface TamaQuestObjectiveProgress {
  id: string;
  current: number;
  required: number;
  completed: boolean;
}

export interface TamaQuestState {
  id: string;
  title: string;
  description?: string;
  status: TamaQuestStatus;
  objectives: TamaQuestObjective[];
  progress: TamaQuestObjectiveProgress[];
  rewards: TamaQuestReward[];
  unlocksOnClaimQuestId?: string;
  completedAt?: number;
  claimedAt?: number;
  updatedAt?: number;
}

export interface TamaQuestLogLike {
  quests?: TamaQuestState[];
  updatedAt?: number;
  [key: string]: unknown;
}

export interface TamaQuestEvent {
  type: TamaQuestObjectiveType;
  target?: string;
  stat?: "energy" | "hunger" | "happiness" | "hygiene" | "health";
  value?: number;
  amount?: number;
}

export interface TamaQuestSyncResult {
  quests: TamaQuestState[];
  changed: boolean;
  completedQuestIds: string[];
}

function cloneObjective(objective: TamaQuestObjective): TamaQuestObjective {
  return { ...objective };
}

function cloneReward(reward: TamaQuestReward): TamaQuestReward {
  return { ...reward };
}

function cloneProgress(progress: TamaQuestObjectiveProgress): TamaQuestObjectiveProgress {
  return { ...progress };
}

function cloneQuest(quest: TamaQuestState): TamaQuestState {
  return {
    ...quest,
    objectives: quest.objectives.map(cloneObjective),
    progress: quest.progress.map(cloneProgress),
    rewards: quest.rewards.map(cloneReward),
  };
}

function ensureQuestLog(target: TamaQuestLogLike): TamaQuestState[] {
  if (!Array.isArray(target.quests)) {
    target.quests = [];
  }

  target.quests = target.quests
    .filter(
      (quest) =>
        !!quest &&
        typeof quest.id === "string" &&
        typeof quest.title === "string" &&
        Array.isArray(quest.objectives) &&
        Array.isArray(quest.progress) &&
        Array.isArray(quest.rewards) &&
        typeof quest.status === "string",
    )
    .map((quest) => cloneQuest(quest));

  return target.quests;
}

function normalizeRequired(value: unknown): number {
  if (typeof value !== "number" || !Number.isFinite(value)) return 1;
  return Math.max(1, Math.floor(value));
}

function normalizeCurrent(value: unknown): number {
  if (typeof value !== "number" || !Number.isFinite(value)) return 0;
  return Math.max(0, Math.floor(value));
}

function isProgressCompleted(current: number, required: number): boolean {
  return current >= required;
}

function createProgressFromObjective(
  objective: TamaQuestObjective,
): TamaQuestObjectiveProgress {
  const required = normalizeRequired(objective.required);
  return {
    id: objective.id,
    current: 0,
    required,
    completed: false,
  };
}

function buildQuestState(
  definition: TamaQuestDefinition,
  now: number,
): TamaQuestState {
  const objectives = definition.objectives.map(cloneObjective);
  const progress = objectives.map(createProgressFromObjective);

  return {
    id: definition.id,
    title: definition.title,
    description: definition.description,
    status: definition.status ?? "active",
    objectives,
    progress,
    rewards: Array.isArray(definition.rewards) ? definition.rewards.map(cloneReward) : [],
    unlocksOnClaimQuestId: definition.unlocksOnClaimQuestId,
    updatedAt: now,
  };
}

function questById(quests: TamaQuestState[], questId: string): TamaQuestState | undefined {
  return quests.find((quest) => quest.id === questId);
}

function objectiveById(
  quest: TamaQuestState,
  objectiveId: string,
): { objective: TamaQuestObjective; progress: TamaQuestObjectiveProgress } | undefined {
  const objective = quest.objectives.find((item) => item.id === objectiveId);
  const progress = quest.progress.find((item) => item.id === objectiveId);

  if (!objective || !progress) return undefined;
  return { objective, progress };
}

function matchesEvent(
  objective: TamaQuestObjective,
  event: TamaQuestEvent,
): boolean {
  if (objective.type !== event.type) return false;
  if (objective.target && objective.target !== event.target) return false;
  if (objective.stat && objective.stat !== event.stat) return false;
  return true;
}

function evaluateImmediateObjective(
  objective: TamaQuestObjective,
  context?: {
    pet?: {
      energy?: number;
      hunger?: number;
      happiness?: number;
      hygiene?: number;
      health?: number;
      mood?: string;
    };
  },
): number | undefined {
  if (!context?.pet) return undefined;

  if (objective.type === "pet-mood") {
    return context.pet.mood === objective.target ? normalizeRequired(objective.required) : 0;
  }

  if (objective.type === "pet-stat-at-least" && objective.stat) {
    const statValue = context.pet[objective.stat];
    const needed = typeof objective.value === "number" ? objective.value : 0;
    if (typeof statValue !== "number" || !Number.isFinite(statValue)) return 0;
    return statValue >= needed ? normalizeRequired(objective.required) : 0;
  }

  return undefined;
}

function refreshQuestStatus(quest: TamaQuestState, now: number): boolean {
  const allCompleted =
    quest.progress.length > 0 && quest.progress.every((item) => item.completed === true);

  if (allCompleted && quest.status === "active") {
    quest.status = "completed";
    quest.completedAt = now;
    quest.updatedAt = now;
    return true;
  }

  return false;
}

export function registerQuests(
  target: TamaQuestLogLike,
  definitions: TamaQuestDefinition[],
  now = Date.now(),
): TamaQuestState[] {
  const quests = ensureQuestLog(target).map(cloneQuest);

  for (const definition of definitions) {
    if (!definition || typeof definition.id !== "string" || !Array.isArray(definition.objectives)) {
      continue;
    }

    if (questById(quests, definition.id)) continue;
    quests.push(buildQuestState(definition, now));
  }

  target.quests = quests;
  target.updatedAt = now;
  return quests.map(cloneQuest);
}

export function listQuests(target: TamaQuestLogLike): TamaQuestState[] {
  return ensureQuestLog(target).map(cloneQuest);
}

export function trackQuestEvent(
  target: TamaQuestLogLike,
  event: TamaQuestEvent,
  now = Date.now(),
  context?: {
    pet?: {
      energy?: number;
      hunger?: number;
      happiness?: number;
      hygiene?: number;
      health?: number;
      mood?: string;
    };
  },
): TamaQuestSyncResult {
  const quests = ensureQuestLog(target).map(cloneQuest);
  let changed = false;
  const completedQuestIds: string[] = [];

  for (const quest of quests) {
    if (quest.status !== "active") continue;

    for (const progress of quest.progress) {
      if (progress.completed) continue;

      const matched = objectiveById(quest, progress.id);
      if (!matched) continue;

      const { objective } = matched;

      const immediate = evaluateImmediateObjective(objective, context);
      if (typeof immediate === "number") {
        const nextCurrent = Math.max(progress.current, immediate);
        if (nextCurrent !== progress.current) {
          progress.current = nextCurrent;
          progress.completed = isProgressCompleted(progress.current, progress.required);
          changed = true;
        }
        continue;
      }

      if (!matchesEvent(objective, event)) continue;

      const increment =
        typeof event.amount === "number" && Number.isFinite(event.amount)
          ? Math.max(1, Math.floor(event.amount))
          : 1;

      const nextCurrent = Math.min(progress.required, progress.current + increment);

      if (nextCurrent !== progress.current) {
        progress.current = nextCurrent;
        progress.completed = isProgressCompleted(progress.current, progress.required);
        changed = true;
      }
    }

    if (refreshQuestStatus(quest, now)) {
      completedQuestIds.push(quest.id);
      changed = true;
    }
  }

  target.quests = quests;
  target.updatedAt = now;

  return {
    quests: quests.map(cloneQuest),
    changed,
    completedQuestIds,
  };
}

export function syncQuestSnapshot(
  target: TamaQuestLogLike,
  now = Date.now(),
  context?: {
    pet?: {
      energy?: number;
      hunger?: number;
      happiness?: number;
      hygiene?: number;
      health?: number;
      mood?: string;
    };
  },
): TamaQuestSyncResult {
  const quests = ensureQuestLog(target).map(cloneQuest);
  let changed = false;
  const completedQuestIds: string[] = [];

  for (const quest of quests) {
    if (quest.status !== "active") continue;

    for (const progress of quest.progress) {
      const matched = objectiveById(quest, progress.id);
      if (!matched) continue;

      const immediate = evaluateImmediateObjective(matched.objective, context);
      if (typeof immediate !== "number") continue;

      const nextCurrent = Math.max(progress.current, immediate);
      if (nextCurrent !== progress.current) {
        progress.current = nextCurrent;
        progress.completed = isProgressCompleted(progress.current, progress.required);
        changed = true;
      }
    }

    if (refreshQuestStatus(quest, now)) {
      completedQuestIds.push(quest.id);
      changed = true;
    }
  }

  target.quests = quests;
  target.updatedAt = now;

  return {
    quests: quests.map(cloneQuest),
    changed,
    completedQuestIds,
  };
}

export function claimQuest(
  target: TamaQuestLogLike,
  questId: string,
  now = Date.now(),
): TamaQuestState | undefined {
  const quests = ensureQuestLog(target).map(cloneQuest);
  const quest = questById(quests, questId);

  if (!quest || quest.status !== "completed") {
    target.quests = quests;
    target.updatedAt = now;
    return undefined;
  }

  quest.status = "claimed";
  quest.claimedAt = now;
  quest.updatedAt = now;

  if (quest.unlocksOnClaimQuestId) {
    const unlockQuest = questById(quests, quest.unlocksOnClaimQuestId);
    if (unlockQuest && unlockQuest.status === "locked") {
      unlockQuest.status = "active";
      unlockQuest.updatedAt = now;
    }
  }

  target.quests = quests;
  target.updatedAt = now;
  return cloneQuest(quest);
}
