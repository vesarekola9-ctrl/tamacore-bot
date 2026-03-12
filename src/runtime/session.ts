import {
  addItem,
  hasItem,
  listInventory,
  removeItem,
  type TamaInventoryEntry,
  type TamaInventoryLike,
} from "./inventory";
import {
  createPetState,
  tickPetState,
  type TamaNeedDecayRates,
  type TamaPetState,
  type TamaTickResult,
} from "./pet-state";
import {
  clearReadNotifications,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  syncPetNotifications,
  type TamaNotification,
  type TamaNotificationsLike,
} from "./notifications";
import { useItem, type TamaUsableItem } from "./use-item";

export interface TamaSessionState extends TamaInventoryLike, TamaNotificationsLike {
  pet: TamaPetState;
  inventory: TamaInventoryEntry[];
  notifications: TamaNotification[];
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

export function createSessionState(
  initial?: Partial<TamaSessionState>,
  now = Date.now(),
): TamaSessionState {
  const session: TamaSessionState = {
    pet: createPetState(initial?.pet, now),
    inventory: cloneInventory(initial?.inventory),
    notifications: cloneNotifications(initial?.notifications),
    createdAt: typeof initial?.createdAt === "number" ? initial.createdAt : now,
    updatedAt: now,
    lastActionAt: typeof initial?.lastActionAt === "number" ? initial.lastActionAt : now,
  };

  const sync = syncPetNotifications(session, session.pet, now);

  return {
    ...session,
    notifications: cloneNotifications(sync.notifications),
    updatedAt: now,
  };
}

export function tickSessionState(
  sessionInput: TamaSessionState,
  now = Date.now(),
  decayRates?: Partial<TamaNeedDecayRates>,
): TamaTickResult & { session: TamaSessionState } {
  const session = createSessionState(sessionInput, now);
  const tick = tickPetState(session.pet, now, decayRates);

  const nextSession: TamaSessionState = {
    ...session,
    pet: tick.pet,
    inventory: cloneInventory(session.inventory),
    notifications: cloneNotifications(session.notifications),
    updatedAt: now,
  };

  const sync = syncPetNotifications(nextSession, nextSession.pet, now);
  nextSession.notifications = cloneNotifications(sync.notifications);

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
  const session = createSessionState(sessionInput, now);
  const result = addItem(session, itemId, quantity, now);

  return {
    session: {
      ...session,
      inventory: cloneInventory(session.inventory),
      notifications: cloneNotifications(session.notifications),
      updatedAt: now,
      lastActionAt: now,
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
  const session = createSessionState(sessionInput, now);

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

  const nextSession: TamaSessionState = {
    ...session,
    pet: createPetState(useResult.pet as TamaPetState, now),
    inventory: cloneInventory(session.inventory),
    notifications: cloneNotifications(session.notifications),
    updatedAt: now,
    lastActionAt: now,
  };

  const sync = syncPetNotifications(nextSession, nextSession.pet, now);
  nextSession.notifications = cloneNotifications(sync.notifications);

  return {
    session: nextSession,
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
  const session = createSessionState(sessionInput, now);
  markNotificationRead(session, id, now);

  return {
    ...session,
    notifications: cloneNotifications(session.notifications),
    updatedAt: now,
  };
}

export function readAllSessionNotifications(
  sessionInput: TamaSessionState,
  now = Date.now(),
): TamaSessionState {
  const session = createSessionState(sessionInput, now);
  markAllNotificationsRead(session, now);

  return {
    ...session,
    notifications: cloneNotifications(session.notifications),
    updatedAt: now,
  };
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
