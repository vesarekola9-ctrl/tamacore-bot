import type { TamaPetState } from "./pet-state";

export type TamaNotificationLevel = "info" | "warning" | "critical";

export interface TamaNotification {
  id: string;
  code: string;
  level: TamaNotificationLevel;
  message: string;
  createdAt: number;
  read: boolean;
}

export interface TamaNotificationsLike {
  notifications?: TamaNotification[];
  updatedAt?: number;
  [key: string]: unknown;
}

export interface TamaNotificationRuleResult {
  notifications: TamaNotification[];
  added: TamaNotification[];
}

function ensureNotifications(target: TamaNotificationsLike): TamaNotification[] {
  if (!Array.isArray(target.notifications)) {
    target.notifications = [];
  }

  target.notifications = target.notifications
    .filter(
      (item) =>
        !!item &&
        typeof item.id === "string" &&
        typeof item.code === "string" &&
        typeof item.level === "string" &&
        typeof item.message === "string" &&
        typeof item.createdAt === "number" &&
        Number.isFinite(item.createdAt) &&
        typeof item.read === "boolean",
    )
    .map((item) => ({
      id: item.id,
      code: item.code,
      level: item.level,
      message: item.message,
      createdAt: item.createdAt,
      read: item.read,
    }));

  return target.notifications;
}

function cloneNotifications(items: TamaNotification[]): TamaNotification[] {
  return items.map((item) => ({ ...item }));
}

function hasUnreadCode(items: TamaNotification[], code: string): boolean {
  return items.some((item) => item.code === code && item.read === false);
}

export function pushNotification(
  target: TamaNotificationsLike,
  input: Omit<TamaNotification, "id" | "createdAt" | "read"> & {
    id?: string;
    createdAt?: number;
    read?: boolean;
  },
  now = Date.now(),
): TamaNotification {
  const notifications = cloneNotifications(ensureNotifications(target));

  const next: TamaNotification = {
    id: input.id ?? `${input.code}:${now}`,
    code: input.code,
    level: input.level,
    message: input.message,
    createdAt: typeof input.createdAt === "number" ? input.createdAt : now,
    read: typeof input.read === "boolean" ? input.read : false,
  };

  notifications.unshift(next);
  target.notifications = notifications;
  target.updatedAt = now;

  return next;
}

export function markNotificationRead(
  target: TamaNotificationsLike,
  id: string,
  now = Date.now(),
): TamaNotification[] {
  const notifications = cloneNotifications(ensureNotifications(target)).map((item) =>
    item.id === id ? { ...item, read: true } : item,
  );

  target.notifications = notifications;
  target.updatedAt = now;
  return notifications;
}

export function markAllNotificationsRead(
  target: TamaNotificationsLike,
  now = Date.now(),
): TamaNotification[] {
  const notifications = cloneNotifications(ensureNotifications(target)).map((item) => ({
    ...item,
    read: true,
  }));

  target.notifications = notifications;
  target.updatedAt = now;
  return notifications;
}

export function listNotifications(target: TamaNotificationsLike): TamaNotification[] {
  return cloneNotifications(ensureNotifications(target));
}

export function clearReadNotifications(
  target: TamaNotificationsLike,
  now = Date.now(),
): TamaNotification[] {
  const notifications = cloneNotifications(ensureNotifications(target)).filter(
    (item) => item.read === false,
  );

  target.notifications = notifications;
  target.updatedAt = now;
  return notifications;
}

export function syncPetNotifications(
  target: TamaNotificationsLike,
  pet: TamaPetState,
  now = Date.now(),
): TamaNotificationRuleResult {
  const notifications = cloneNotifications(ensureNotifications(target));
  const added: TamaNotification[] = [];

  const addRule = (
    code: string,
    level: TamaNotificationLevel,
    message: string,
    condition: boolean,
  ): void => {
    if (!condition) return;
    if (hasUnreadCode(notifications, code)) return;

    const next: TamaNotification = {
      id: `${code}:${now}`,
      code,
      level,
      message,
      createdAt: now,
      read: false,
    };

    notifications.unshift(next);
    added.push(next);
  };

  addRule("pet:critical-health", "critical", "Pet health is critical.", pet.health <= 20);
  addRule("pet:hungry", "warning", "Pet is hungry.", pet.hunger <= 30);
  addRule("pet:tired", "warning", "Pet is tired.", pet.energy <= 30);
  addRule("pet:dirty", "warning", "Pet is dirty.", pet.hygiene <= 30);
  addRule("pet:sad", "info", "Pet needs attention.", pet.happiness <= 30);
  addRule("pet:great-mood", "info", "Pet is feeling great.", pet.mood === "great");

  target.notifications = notifications;
  target.updatedAt = now;

  return {
    notifications,
    added,
  };
}
