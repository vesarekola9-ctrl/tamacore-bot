import {
  bootstrapBridgeSession,
  bridgeClaimQuest,
  bridgeConsumeEvents,
  bridgeTickSession,
  createBridgeSnapshot,
  type TamaBridgeBootstrapInput,
  type TamaBridgeSnapshot,
} from "./bridge";
import { getSessionEvents, type TamaSessionState } from "./session";
import { resolveRuntimeConfig, type TamaResolvedRuntimeConfig } from "./runtime-config";

export interface TamaLiveLoopState {
  session: TamaSessionState;
  config: TamaResolvedRuntimeConfig;
  startedAt: number;
  updatedAt: number;
  tickCount: number;
}

export interface TamaLiveLoopTickResult {
  state: TamaLiveLoopState;
  snapshot: TamaBridgeSnapshot;
  consumedEventCount: number;
  claimedQuestIds: string[];
}

function enforceEventLimit(
  session: TamaSessionState,
  limit: number,
  now: number,
): TamaSessionState {
  const events = getSessionEvents(session);
  if (events.length <= limit) return session;

  const overflow = events.length - limit;
  return bridgeConsumeEvents(session, overflow, now).session;
}

function autoClaimCompletedQuests(
  state: TamaLiveLoopState,
  now: number,
): { session: TamaSessionState; claimedQuestIds: string[] } {
  if (!state.config.loop.questAutoClaim) {
    return {
      session: state.session,
      claimedQuestIds: [],
    };
  }

  let session = state.session;
  const claimedQuestIds: string[] = [];

  for (const quest of session.quests) {
    if (quest.status !== "completed") continue;
    session = bridgeClaimQuest(session, quest.id, now).session;
    claimedQuestIds.push(quest.id);
  }

  return {
    session,
    claimedQuestIds,
  };
}

export function createLiveLoop(
  input?: TamaBridgeBootstrapInput & {
    decay?: Partial<TamaResolvedRuntimeConfig["decay"]>;
    loop?: Partial<TamaResolvedRuntimeConfig["loop"]>;
  },
): TamaLiveLoopState {
  const now = typeof input?.now === "number" ? input.now : Date.now();
  const resolved = resolveRuntimeConfig({
    pet: input?.pet,
    items: input?.items,
    quests: input?.quests,
    inventory: input?.inventory,
    coins: input?.coins,
    decay: input?.decay,
    loop: input?.loop,
  });

  const boot = bootstrapBridgeSession({
    pet: resolved.config.pet,
    items: resolved.config.items,
    quests: resolved.config.quests,
    inventory: resolved.config.inventory,
    coins: resolved.config.coins,
    now,
  });

  return {
    session: boot.session,
    config: resolved.config,
    startedAt: now,
    updatedAt: now,
    tickCount: 0,
  };
}

export function tickLiveLoop(
  input: TamaLiveLoopState,
  now = Date.now(),
): TamaLiveLoopTickResult {
  let session = bridgeTickSession(input.session, now, input.config.decay).session;

  const autoClaim = autoClaimCompletedQuests(
    {
      ...input,
      session,
    },
    now,
  );

  session = autoClaim.session;
  session = enforceEventLimit(session, input.config.loop.eventQueueLimit, now);

  const state: TamaLiveLoopState = {
    ...input,
    session,
    updatedAt: now,
    tickCount: input.tickCount + 1,
  };

  return {
    state,
    snapshot: createBridgeSnapshot(session),
    consumedEventCount: Math.max(0, getSessionEvents(session).length - input.config.loop.eventQueueLimit),
    claimedQuestIds: autoClaim.claimedQuestIds,
  };
}
