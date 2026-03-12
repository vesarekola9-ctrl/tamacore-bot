export type TamaSessionEventType =
  | "session-created"
  | "session-ticked"
  | "coins-granted"
  | "item-granted"
  | "item-bought"
  | "item-used"
  | "notification-read"
  | "notifications-read-all"
  | "notifications-cleared-read"
  | "quests-registered"
  | "quest-claimed";

export interface TamaSessionEvent<TPayload = Record<string, unknown>> {
  id: string;
  type: TamaSessionEventType;
  createdAt: number;
  payload: TPayload;
}

export interface TamaSessionEventsLike {
  events?: TamaSessionEvent[];
  updatedAt?: number;
  [key: string]: unknown;
}

export interface TamaPushEventInput<TPayload = Record<string, unknown>> {
  type: TamaSessionEventType;
  payload: TPayload;
  id?: string;
  createdAt?: number;
}

function cloneEvent<TPayload = Record<string, unknown>>(
  event: TamaSessionEvent<TPayload>,
): TamaSessionEvent<TPayload> {
  return {
    ...event,
    payload:
      event.payload && typeof event.payload === "object"
        ? ({ ...(event.payload as Record<string, unknown>) } as TPayload)
        : event.payload,
  };
}

function isValidEvent(value: unknown): value is TamaSessionEvent {
  if (!value || typeof value !== "object") return false;
  const event = value as Record<string, unknown>;

  return (
    typeof event.id === "string" &&
    typeof event.type === "string" &&
    typeof event.createdAt === "number" &&
    Number.isFinite(event.createdAt) &&
    "payload" in event
  );
}

export function ensureSessionEvents(target: TamaSessionEventsLike): TamaSessionEvent[] {
  if (!Array.isArray(target.events)) {
    target.events = [];
  }

  target.events = target.events.filter(isValidEvent).map((event) => cloneEvent(event));
  return target.events;
}

export function listSessionEvents(target: TamaSessionEventsLike): TamaSessionEvent[] {
  return ensureSessionEvents(target).map((event) => cloneEvent(event));
}

export function pushSessionEvent<TPayload = Record<string, unknown>>(
  target: TamaSessionEventsLike,
  input: TamaPushEventInput<TPayload>,
  now = Date.now(),
): TamaSessionEvent<TPayload> {
  const events = ensureSessionEvents(target).map((event) => cloneEvent(event));
  const next: TamaSessionEvent<TPayload> = {
    id: input.id ?? `${input.type}:${now}:${events.length}`,
    type: input.type,
    createdAt: typeof input.createdAt === "number" ? input.createdAt : now,
    payload: input.payload,
  };

  events.unshift(next as TamaSessionEvent);
  target.events = events;
  target.updatedAt = now;

  return cloneEvent(next);
}

export function clearSessionEvents(
  target: TamaSessionEventsLike,
  now = Date.now(),
): TamaSessionEvent[] {
  target.events = [];
  target.updatedAt = now;
  return [];
}

export function shiftSessionEvents(
  target: TamaSessionEventsLike,
  count = 1,
  now = Date.now(),
): TamaSessionEvent[] {
  const events = ensureSessionEvents(target).map((event) => cloneEvent(event));
  const safeCount =
    typeof count === "number" && Number.isFinite(count) ? Math.max(0, Math.floor(count)) : 0;

  const next = events.slice(safeCount);
  target.events = next;
  target.updatedAt = now;
  return next.map((event) => cloneEvent(event));
}
