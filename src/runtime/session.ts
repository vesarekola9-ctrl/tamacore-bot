import {
  getCatalogItem,
  listCatalogItems,
  registerCatalogItems,
  type TamaCatalogItem,
  type TamaCatalogLike,
} from "./catalog";
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
import {
  clearSessionEvents,
  listSessionEvents,
  pushSessionEvent,
  shiftSessionEvents,
  type TamaSessionEvent,
  type TamaSessionEventsLike,
} from "./session-events";
import { buyCatalogItem, getCoins, grantCoins, type TamaWalletLike } from "./shop";
import { useItem, type TamaUsableItem } from "./use-item";

export interface TamaSessionState
  extends TamaInventoryLike,
    TamaNotificationsLike,
    TamaQuestLogLike,
    TamaCatalogLike,
    TamaWalletLike,
    TamaSessionEventsLike {
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

export interface TamaBuyItemResult {
  session: TamaSessionState;
  success: boolean;
  reason?: "ITEM_NOT_FOUND" | "ITEM_HAS_NO_PRICE" | "NOT_ENOUGH_COINS";
  itemId?: string;
  remainingCoins?: number;
  nextQuantity?: number;
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

function cloneCatalog(entries?: TamaCatalogItem[]): TamaCatalogItem[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({
    ...entry,
    changes: Array.isArray(entry.changes) ? entry.changes.map((change) => ({ ...change })) : [],
    timedEffects: Array.isArray(entry.timedEffects)
      ? entry.timedEffects.map((effect) => ({ ...effect }))
      : [],
    tags: Array.isArray(entry.tags) ? [...entry.tags] : [],
  }));
}

function cloneEvents(entries?: TamaSessionEvent[]): TamaSessionEvent[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({
    ...entry,
    payload:
      entry.payload && typeof entry.payload === "object"
        ? { ...(entry.payload as Record<string, unknown>) }
        : entry.payload,
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
    items: cloneCatalog(initial?.items),
    events: cloneEvents(initial?.events),
    coins:
      typeof initial?.coins === "number" && Number.isFinite(initial.coins)
        ? Math.max(0, Math.floor(initial.coins))
        : 0,
    createdAt: typeof initial?.createdAt === "number" ? initial.createdAt : now,
    updatedAt: now,
    lastActionAt: typeof initial?.lastActionAt === "number" ? initial.lastActionAt : now,
  };

  const next = syncSessionDerivedState(session, now);

  if (!initial) {
    pushSessionEvent(
      next,
      {
        type: "session-created",
        payload: {
          createdAt: next.createdAt,
        },
      },
      now,
    );
  }

  return next;
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
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
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

  pushSessionEvent(
    nextSession,
    {
      type: "session-ticked",
      payload: {
        elapsedMs: tick.elapsedMs,
        elapsedMinutes: tick.elapsedMinutes,
        changedNeeds: [...tick.changedNeeds],
        mood: nextSession.pet.mood,
      },
    },
    now,
  );

  return {
    ...tick,
    session: {
      ...nextSession,
      events: cloneEvents(nextSession.events),
    },
  };
}

export function registerSessionCatalog(
  sessionInput: TamaSessionState,
  items: TamaCatalogItem[],
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  registerCatalogItems(session, items, now);

  return {
    ...session,
    items: cloneCatalog(listCatalogItems(session)),
    events: cloneEvents(session.events),
    updatedAt: now,
  };
}

export function getSessionCatalog(
  sessionInput: TamaSessionState,
): TamaCatalogItem[] {
  const session = createSessionState(sessionInput);
  return listCatalogItems(session);
}

export function grantSessionCoins(
  sessionInput: TamaSessionState,
  amount: number,
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  const before = getCoins(session);
  grantCoins(session, amount, now);
  const after = getCoins(session);

  pushSessionEvent(
    session,
    {
      type: "coins-granted",
      payload: {
        amount: Math.max(0, after - before),
        coinsBefore: before,
        coinsAfter: after,
      },
    },
    now,
  );

  return {
    ...session,
    coins: getCoins(session),
    events: cloneEvents(session.events),
    updatedAt: now,
    lastActionAt: now,
  };
}

export function getSessionCoins(sessionInput: TamaSessionState): number {
  const session = createSessionState(sessionInput);
  return getCoins(session);
}

export function buySessionItem(
  sessionInput: TamaSessionState,
  itemId: string,
  now = Date.now(),
): TamaBuyItemResult {
  let session = createSessionState(sessionInput, now);

  const result = buyCatalogItem(session, itemId, now);

  if (!result.success) {
    return {
      session,
      success: false,
      reason: result.reason,
      remainingCoins: result.remainingCoins ?? getCoins(session),
    };
  }

  const tracked = trackQuestEvent(
    session,
    { type: "gain-item", target: itemId, amount: 1 },
    now,
    { pet: session.pet },
  );

  session = {
    ...session,
    inventory: cloneInventory(session.inventory),
    notifications: cloneNotifications(session.notifications),
    quests: cloneQuests(tracked.quests),
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
    updatedAt: now,
    lastActionAt: now,
  };

  const entry = session.inventory.find((item) => item.itemId === itemId);

  pushSessionEvent(
    session,
    {
      type: "item-bought",
      payload: {
        itemId,
        paidCoins: result.paidCoins ?? 0,
        remainingCoins: getCoins(session),
        nextQuantity: entry ? entry.quantity : 0,
      },
    },
    now,
  );

  return {
    session: {
      ...session,
      events: cloneEvents(session.events),
    },
    success: true,
    itemId,
    remainingCoins: getCoins(session),
    nextQuantity: entry ? entry.quantity : 0,
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
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
    updatedAt: now,
    lastActionAt: now,
  };

  pushSessionEvent(
    session,
    {
      type: "item-granted",
      payload: {
        itemId,
        quantity,
        nextQuantity: result.nextQuantity,
      },
    },
    now,
  );

  return {
    session: {
      ...session,
      events: cloneEvents(session.events),
    },
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
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
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

  pushSessionEvent(
    session,
    {
      type: "item-used",
      payload: {
        itemId: item.id,
        remainingQuantity: removal.nextQuantity,
        mood: session.pet.mood,
      },
    },
    now,
  );

  return {
    session: {
      ...session,
      events: cloneEvents(session.events),
    },
    success: true,
    usedItemId: item.id,
    remainingQuantity: removal.nextQuantity,
  };
}

export function useSessionCatalogItem(
  sessionInput: TamaSessionState,
  itemId: string,
  now = Date.now(),
): TamaUseInventoryItemResult {
  const session = createSessionState(sessionInput, now);
  const item = getCatalogItem(session, itemId);

  if (!item) {
    return {
      session,
      success: false,
      reason: "ITEM_NOT_USABLE",
    };
  }

  return useInventoryItem(session, item, now);
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
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
    updatedAt: now,
  };

  pushSessionEvent(
    session,
    {
      type: "notification-read",
      payload: {
        notificationId: id,
      },
    },
    now,
  );

  return {
    ...session,
    events: cloneEvents(session.events),
  };
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
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
    updatedAt: now,
  };

  pushSessionEvent(
    session,
    {
      type: "notifications-read-all",
      payload: {
        count: beforeUnread,
      },
    },
    now,
  );

  return {
    ...session,
    events: cloneEvents(session.events),
  };
}

export function clearSessionReadNotifications(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  const before = session.notifications.length;
  clearReadNotifications(session, now);
  const after = session.notifications.length;

  pushSessionEvent(
    session,
    {
      type: "notifications-cleared-read",
      payload: {
        removedCount: Math.max(0, before - after),
      },
    },
    now,
  );

  return {
    ...session,
    notifications: cloneNotifications(session.notifications),
    items: cloneCatalog(session.items),
    events: cloneEvents(session.events),
    coins: getCoins(session),
    updatedAt: now,
  };
}

export function registerSessionQuests(
  sessionInput: TamaSessionState,
  definitions: TamaQuestDefinition[],
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  const before = session.quests.length;
  registerQuests(session, definitions, now);
  const after = session.quests.length;

  pushSessionEvent(
    session,
    {
      type: "quests-registered",
      payload: {
        addedCount: Math.max(0, after - before),
      },
    },
    now,
  );

  return syncSessionDerivedState(
    {
      ...session,
      quests: cloneQuests(session.quests),
      items: cloneCatalog(session.items),
      events: cloneEvents(session.events),
      coins: getCoins(session),
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
      items: cloneCatalog(session.items),
      events: cloneEvents(session.events),
      coins: getCoins(session),
      updatedAt: now,
      lastActionAt: now,
    },
    now,
  );

  pushSessionEvent(
    session,
    {
      type: "quest-claimed",
      payload: {
        questId,
        rewards: claimed.rewards.map((reward) => ({
          itemId: reward.itemId,
          quantity: reward.quantity,
        })),
      },
    },
    now,
  );

  return {
    ...session,
    events: cloneEvents(session.events),
  };
}

export function getSessionEvents(
  sessionInput: TamaSessionState,
): TamaSessionEvent[] {
  const session = createSessionState(sessionInput);
  return listSessionEvents(session);
}

export function clearAllSessionEvents(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  clearSessionEvents(session, now);

  return {
    ...session,
    events: cloneEvents(session.events),
    updatedAt: now,
  };
}

export function consumeSessionEvents(
  sessionInput: TamaSessionState,
  count = 1,
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  shiftSessionEvents(session, count, now);

  return {
    ...session,
    events: cloneEvents(session.events),
    updatedAt: now,
  };
}
