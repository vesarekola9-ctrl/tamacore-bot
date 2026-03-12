import type { TamaCatalogItem } from "./catalog";
import type { TamaInventoryEntry } from "./inventory";
import type { TamaNotification } from "./notifications";
import type { TamaPetState } from "./pet-state";
import type { TamaQuestState } from "./quests";
import {
  claimSessionQuest,
  clearAllSessionEvents,
  clearSessionReadNotifications,
  consumeSessionEvents,
  createSessionState,
  getSessionCatalog,
  getSessionCoins,
  getSessionEvents,
  getSessionInventory,
  getSessionNotifications,
  getSessionQuests,
  grantInventoryItem,
  grantSessionCoins,
  registerSessionCatalog,
  registerSessionQuests,
  tickSessionState,
  useSessionCatalogItem,
  readAllSessionNotifications,
  readSessionNotification,
  type TamaBuyItemResult,
  type TamaGrantItemResult,
  type TamaSessionState,
  type TamaUseInventoryItemResult,
  buySessionItem,
} from "./session";
import type { TamaQuestDefinition } from "./quests";
import type { TamaSessionEvent } from "./session-events";
import type { TamaNeedDecayRates, TamaTickResult } from "./pet-state";
import {
  validateRuntimeBootstrapConfig,
  type TamaRuntimeValidationIssue,
} from "./validator";

export interface TamaBridgeBootstrapInput {
  pet?: Partial<TamaPetState>;
  items?: TamaCatalogItem[];
  quests?: TamaQuestDefinition[];
  coins?: number;
  inventory?: TamaInventoryEntry[];
  now?: number;
}

export interface TamaBridgeSnapshot {
  pet: TamaPetState;
  inventory: TamaInventoryEntry[];
  notifications: TamaNotification[];
  quests: TamaQuestState[];
  items: TamaCatalogItem[];
  events: TamaSessionEvent[];
  coins: number;
  createdAt: number;
  updatedAt: number;
  lastActionAt: number;
}

export interface TamaBridgeResult<T = Record<string, unknown>> {
  session: TamaSessionState;
  snapshot: TamaBridgeSnapshot;
  result: T;
}

export interface TamaBridgeBootstrapResult {
  bootstrapped: boolean;
  valid: boolean;
  issues: TamaRuntimeValidationIssue[];
}

function cloneInventory(entries: TamaInventoryEntry[]): TamaInventoryEntry[] {
  return entries.map((entry) => ({
    itemId: entry.itemId,
    quantity: entry.quantity,
  }));
}

function cloneNotifications(entries: TamaNotification[]): TamaNotification[] {
  return entries.map((entry) => ({ ...entry }));
}

function cloneQuests(entries: TamaQuestState[]): TamaQuestState[] {
  return entries.map((entry) => ({
    ...entry,
    objectives: entry.objectives.map((objective) => ({ ...objective })),
    progress: entry.progress.map((progress) => ({ ...progress })),
    rewards: entry.rewards.map((reward) => ({ ...reward })),
  }));
}

function cloneCatalog(entries: TamaCatalogItem[]): TamaCatalogItem[] {
  return entries.map((entry) => ({
    ...entry,
    changes: Array.isArray(entry.changes) ? entry.changes.map((change) => ({ ...change })) : [],
    timedEffects: Array.isArray(entry.timedEffects)
      ? entry.timedEffects.map((effect) => ({ ...effect }))
      : [],
    tags: Array.isArray(entry.tags) ? [...entry.tags] : [],
  }));
}

function cloneEvents(entries: TamaSessionEvent[]): TamaSessionEvent[] {
  return entries.map((entry) => ({
    ...entry,
    payload:
      entry.payload && typeof entry.payload === "object"
        ? { ...(entry.payload as Record<string, unknown>) }
        : entry.payload,
  }));
}

export function createBridgeSnapshot(session: TamaSessionState): TamaBridgeSnapshot {
  return {
    pet: { ...session.pet, activeEffects: Array.isArray(session.pet.activeEffects) ? [...session.pet.activeEffects] : [] },
    inventory: cloneInventory(getSessionInventory(session)),
    notifications: cloneNotifications(getSessionNotifications(session)),
    quests: cloneQuests(getSessionQuests(session)),
    items: cloneCatalog(getSessionCatalog(session)),
    events: cloneEvents(getSessionEvents(session)),
    coins: getSessionCoins(session),
    createdAt: session.createdAt,
    updatedAt: session.updatedAt,
    lastActionAt: session.lastActionAt,
  };
}

export function bootstrapBridgeSession(
  input?: TamaBridgeBootstrapInput,
): TamaBridgeResult<TamaBridgeBootstrapResult> {
  const now = typeof input?.now === "number" ? input.now : Date.now();
  const validation = validateRuntimeBootstrapConfig({
    pet: input?.pet,
    items: input?.items,
    quests: input?.quests,
    inventory: input?.inventory,
    coins: input?.coins,
  });

  let session = createSessionState(
    {
      pet: input?.pet,
      inventory: Array.isArray(input?.inventory) ? cloneInventory(input.inventory) : [],
      coins: typeof input?.coins === "number" ? input.coins : 0,
    },
    now,
  );

  if (Array.isArray(input?.items) && input.items.length > 0) {
    session = registerSessionCatalog(session, input.items, now);
  }

  if (Array.isArray(input?.quests) && input.quests.length > 0) {
    session = registerSessionQuests(session, input.quests, now);
  }

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      bootstrapped: true,
      valid: validation.ok,
      issues: validation.issues,
    },
  };
}

export function bridgeTickSession(
  sessionInput: TamaSessionState,
  now = Date.now(),
  decayRates?: Partial<TamaNeedDecayRates>,
): TamaBridgeResult<TamaTickResult> {
  const tick = tickSessionState(sessionInput, now, decayRates);

  return {
    session: tick.session,
    snapshot: createBridgeSnapshot(tick.session),
    result: {
      pet: tick.pet,
      elapsedMs: tick.elapsedMs,
      elapsedMinutes: tick.elapsedMinutes,
      changedNeeds: [...tick.changedNeeds],
    },
  };
}

export function bridgeGrantCoins(
  sessionInput: TamaSessionState,
  amount: number,
  now = Date.now(),
): TamaBridgeResult<{ amount: number; coins: number }> {
  const session = grantSessionCoins(sessionInput, amount, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      amount,
      coins: getSessionCoins(session),
    },
  };
}

export function bridgeGrantItem(
  sessionInput: TamaSessionState,
  itemId: string,
  quantity = 1,
  now = Date.now(),
): TamaBridgeResult<Omit<TamaGrantItemResult, "session">> {
  const result = grantInventoryItem(sessionInput, itemId, quantity, now);

  return {
    session: result.session,
    snapshot: createBridgeSnapshot(result.session),
    result: {
      itemId: result.itemId,
      quantity: result.quantity,
      nextQuantity: result.nextQuantity,
    },
  };
}

export function bridgeBuyItem(
  sessionInput: TamaSessionState,
  itemId: string,
  now = Date.now(),
): TamaBridgeResult<Omit<TamaBuyItemResult, "session">> {
  const result = buySessionItem(sessionInput, itemId, now);

  return {
    session: result.session,
    snapshot: createBridgeSnapshot(result.session),
    result: {
      success: result.success,
      reason: result.reason,
      itemId: result.itemId,
      remainingCoins: result.remainingCoins,
      nextQuantity: result.nextQuantity,
    },
  };
}

export function bridgeUseItem(
  sessionInput: TamaSessionState,
  itemId: string,
  now = Date.now(),
): TamaBridgeResult<Omit<TamaUseInventoryItemResult, "session">> {
  const result = useSessionCatalogItem(sessionInput, itemId, now);

  return {
    session: result.session,
    snapshot: createBridgeSnapshot(result.session),
    result: {
      success: result.success,
      reason: result.reason,
      usedItemId: result.usedItemId,
      remainingQuantity: result.remainingQuantity,
    },
  };
}

export function bridgeReadNotification(
  sessionInput: TamaSessionState,
  id: string,
  now = Date.now(),
): TamaBridgeResult<{ notificationId: string }> {
  const session = readSessionNotification(sessionInput, id, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      notificationId: id,
    },
  };
}

export function bridgeReadAllNotifications(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaBridgeResult<{ readAll: true }> {
  const session = readAllSessionNotifications(sessionInput, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      readAll: true,
    },
  };
}

export function bridgeClearReadNotifications(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaBridgeResult<{ cleared: true }> {
  const session = clearSessionReadNotifications(sessionInput, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      cleared: true,
    },
  };
}

export function bridgeClaimQuest(
  sessionInput: TamaSessionState,
  questId: string,
  now = Date.now(),
): TamaBridgeResult<{ questId: string }> {
  const session = claimSessionQuest(sessionInput, questId, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      questId,
    },
  };
}

export function bridgeConsumeEvents(
  sessionInput: TamaSessionState,
  count = 1,
  now = Date.now(),
): TamaBridgeResult<{ consumed: number }> {
  const session = consumeSessionEvents(sessionInput, count, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      consumed: Math.max(0, Math.floor(count)),
    },
  };
}

export function bridgeClearEvents(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaBridgeResult<{ cleared: true }> {
  const session = clearAllSessionEvents(sessionInput, now);

  return {
    session,
    snapshot: createBridgeSnapshot(session),
    result: {
      cleared: true,
    },
  };
}
