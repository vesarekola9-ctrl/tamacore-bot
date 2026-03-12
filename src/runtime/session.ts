import {
  addItem,
  hasItem,
  listInventory,
  removeItem,
  type TamaInventoryEntry,
  type TamaInventoryLike,
} from "./inventory";
import {
  clearReadNotifications,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  syncPetNotifications,
  type TamaNotification,
  type TamaNotificationsLike,
} from "./notifications";
import {
  createPetState,
  tickPetState,
  type TamaNeedDecayRates,
  type TamaPetState,
  type TamaTickResult,
} from "./pet-state";
import {
  claimQuest,
  listQuests,
  registerQuests,
  syncQuestSnapshot,
  trackQuestEvent,
  type TamaQuestDefinition,
  type TamaQuestLogLike,
  type TamaQuestState,
} from "./quests";
import { useItem, type TamaUsableItem } from "./use-item";

export interface TamaSessionState
  extends TamaInventoryLike,
    TamaNotificationsLike,
    TamaQuestLogLike {
  pet: TamaPetState;
  inventory: TamaInventoryEntry[];
  notifications: TamaNotification[];
  quests: TamaQuestState[];
  createdAt: number;
  updatedAt: number;
  lastActionAt: number;
}

export interface TamaUseInventoryItemResult {
  session: TamaSessionState;
  success: boolean;
  reason?: "NOT_IN_INVENTORY" | "ITEM_NOT_USABLE";
  usedItemId?: string;
  remainingQuantity?: number;
}

export interface TamaGrantItemResult {
  session: TamaSessionState;
  itemId: string;
  quantity: number;
  nextQuantity: number;
}

function cloneInventory(entries?: TamaInventoryEntry[]): TamaInventoryEntry[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({
    itemId: entry.itemId,
    quantity: entry.quantity,
  }));
}

function cloneNotifications(entries?: TamaNotification[]): TamaNotification[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({ ...entry }));
}

function cloneQuests(entries?: TamaQuestState[]): TamaQuestState[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({
    ...entry,
    objectives: entry.objectives.map((objective) => ({ ...objective })),
    progress: entry.progress.map((progress) => ({ ...progress })),
    rewards: entry.rewards.map((reward) => ({ ...reward })),
  }));
}

function syncSessionDerivedState(
  session: TamaSessionState,
  now: number,
): TamaSessionState {
  const notificationSync = syncPetNotifications(session, session.pet, now);
  const questSync = syncQuestSnapshot(session, now, { pet: session.pet });

  return {
    ...session,
    notifications: cloneNotifications(notificationSync.notifications),
    quests: cloneQuests(questSync.quests),
    updatedAt: now,
  };
}

export function createSessionState(
  initial?: Partial<TamaSessionState>,
  now = Date.now(),
): TamaSessionState {
  const session: TamaSessionState = {
    pet: createPetState(initial?.pet, now),
    inventory: cloneInventory(initial?.inventory),
    notifications: cloneNotifications(initial?.notifications),
    quests: cloneQuests(initial?.quests),
    createdAt: typeof initial?.createdAt === "number" ? initial.createdAt : now,
    updatedAt: now,
    lastActionAt: typeof initial?.lastActionAt === "number" ? initial.lastActionAt : now,
  };

  return syncSessionDerivedState(session, now);
}

export function tickSessionState(
  sessionInput: TamaSessionState,
  now = Date.now(),
  decayRates?: Partial<TamaNeedDecayRates>,
): TamaTickResult & { session: TamaSessionState } {
  const session = createSessionState(sessionInput, now);
  const tick = tickPetState(session.pet, now, decayRates);

  let nextSession: TamaSessionState = {
    ...session,
    pet: tick.pet,
    inventory: cloneInventory(session.inventory),
    notifications: cloneNotifications(session.notifications),
    quests: cloneQuests(session.quests),
    updatedAt: now,
  };

  nextSession = syncSessionDerivedState(nextSession, now);

  const tracked = trackQuestEvent(
    nextSession,
    { type: "tick-session", amount: 1 },
    now,
    { pet: nextSession.pet },
  );

  nextSession.quests = cloneQuests(tracked.quests);

  return {
    ...tick,
    session: nextSession,
  };
}

export function grantInventoryItem(
  sessionInput: TamaSessionState,
  itemId: string,
  quantity = 1,
  now = Date.now(),
): TamaGrantItemResult {
  let session = createSessionState(sessionInput, now);
  const result = addItem(session, itemId, quantity, now);

  const tracked = trackQuestEvent(
    session,
    { type: "gain-item", target: itemId, amount: quantity },
    now,
    { pet: session.pet },
  );

  session = {
    ...session,
    inventory: cloneInventory(session.inventory),
    notifications: cloneNotifications(session.notifications),
    quests: cloneQuests(tracked.quests),
    updatedAt: now,
    lastActionAt: now,
  };

  return {
    session,
    itemId,
    quantity,
    nextQuantity: result.nextQuantity,
  };
}

export function canUseInventoryItem(
  sessionInput: TamaSessionState,
  itemId: string,
): boolean {
  const session = createSessionState(sessionInput);
  return hasItem(session, itemId, 1);
}

export function useInventoryItem(
  sessionInput: TamaSessionState,
  item: TamaUsableItem,
  now = Date.now(),
): TamaUseInventoryItemResult {
  let session = createSessionState(sessionInput, now);

  if (!item || typeof item.id !== "string" || item.id.length === 0) {
    return {
      session,
      success: false,
      reason: "ITEM_NOT_USABLE",
    };
  }

  if (!hasItem(session, item.id, 1)) {
    return {
      session,
      success: false,
      reason: "NOT_IN_INVENTORY",
    };
  }

  const useResult = useItem(session.pet, item, now);

  if (!useResult.consumed) {
    return {
      session,
      success: false,
      reason: "ITEM_NOT_USABLE",
    };
  }

  const removal = removeItem(session, item.id, 1, now);

  session = {
    ...session,
    pet: createPetState(useResult.pet as TamaPetState, now),
    inventory: cloneInventory(session.inventory),
    notifications: cloneNotifications(session.notifications),
    quests: cloneQuests(session.quests),
    updatedAt: now,
    lastActionAt: now,
  };

  session = syncSessionDerivedState(session, now);

  const tracked = trackQuestEvent(
    session,
    { type: "use-item", target: item.id, amount: 1 },
    now,
    { pet: session.pet },
  );

  session = {
    ...session,
    quests: cloneQuests(tracked.quests),
    updatedAt: now,
  };

  return {
    session,
    success: true,
    usedItemId: item.id,
    remainingQuantity: removal.nextQuantity,
  };
}

export function getSessionInventory(
  sessionInput: TamaSessionState,
): TamaInventoryEntry[] {
  const session = createSessionState(sessionInput);
  return listInventory(session);
}

export function getSessionNotifications(
  sessionInput: TamaSessionState,
): TamaNotification[] {
  const session = createSessionState(sessionInput);
  return listNotifications(session);
}

export function readSessionNotification(
  sessionInput: TamaSessionState,
  id: string,
  now = Date.now(),
): TamaSessionState {
  let session = createSessionState(sessionInput, now);
  markNotificationRead(session, id, now);

  const tracked = trackQuestEvent(
    session,
    { type: "read-notification", amount: 1 },
    now,
    { pet: session.pet },
  );

  session = {
    ...session,
    notifications: cloneNotifications(session.notifications),
    quests: cloneQuests(tracked.quests),
    updatedAt: now,
  };

  return session;
}

export function readAllSessionNotifications(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaSessionState {
  let session = createSessionState(sessionInput, now);
  const beforeUnread = session.notifications.filter((item) => item.read === false).length;

  markAllNotificationsRead(session, now);

  const tracked = trackQuestEvent(
    session,
    { type: "read-notification", amount: beforeUnread },
    now,
    { pet: session.pet },
  );

  session = {
    ...session,
    notifications: cloneNotifications(session.notifications),
    quests: cloneQuests(tracked.quests),
    updatedAt: now,
  };

  return session;
}

export function clearSessionReadNotifications(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  clearReadNotifications(session, now);

  return {
    ...session,
    notifications: cloneNotifications(session.notifications),
    updatedAt: now,
  };
}

export function registerSessionQuests(
  sessionInput: TamaSessionState,
  definitions: TamaQuestDefinition[],
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  registerQuests(session, definitions, now);

  return syncSessionDerivedState(
    {
      ...session,
      quests: cloneQuests(session.quests),
      updatedAt: now,
    },
    now,
  );
}

export function getSessionQuests(
  sessionInput: TamaSessionState,
): TamaQuestState[] {
  const session = createSessionState(sessionInput);
  return listQuests(session);
}

export function claimSessionQuest(
  sessionInput: TamaSessionState,
  questId: string,
  now = Date.now(),
): TamaSessionState {
  let session = createSessionState(sessionInput, now);
  const claimed = claimQuest(session, questId, now);

  if (!claimed) {
    return session;
  }

  for (const reward of claimed.rewards) {
    addItem(session, reward.itemId, reward.quantity, now);
  }

  session = syncSessionDerivedState(
    {
      ...session,
      inventory: cloneInventory(session.inventory),
      quests: cloneQuests(session.quests),
      updatedAt: now,
      lastActionAt: now,
    },
    now,
  );

  return session;
}
