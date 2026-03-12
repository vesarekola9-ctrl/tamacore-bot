import type { TamaNotification } from "./notifications";
import type { TamaSessionEvent } from "./session-events";

export interface TamaPrunableState {
  notifications?: TamaNotification[];
  events?: TamaSessionEvent[];
  updatedAt?: number;
  [key: string]: unknown;
}

function cloneNotifications(entries?: TamaNotification[]): TamaNotification[] {
  if (!Array.isArray(entries)) return [];
  return entries.map((entry) => ({ ...entry }));
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

export function pruneNotifications(
  target: TamaPrunableState,
  limit: number,
  now = Date.now(),
): TamaNotification[] {
  const safeLimit =
    typeof limit === "number" && Number.isFinite(limit)
      ? Math.max(0, Math.floor(limit))
      : 0;

  const next = cloneNotifications(target.notifications).slice(0, safeLimit);
  target.notifications = next;
  target.updatedAt = now;
  return next;
}

export function pruneSessionEvents(
  target: TamaPrunableState,
  limit: number,
  now = Date.now(),
): TamaSessionEvent[] {
  const safeLimit =
    typeof limit === "number" && Number.isFinite(limit)
      ? Math.max(0, Math.floor(limit))
      : 0;

  const next = cloneEvents(target.events).slice(0, safeLimit);
  target.events = next;
  target.updatedAt = now;
  return next;
}
