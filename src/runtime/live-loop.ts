import {
  bootstrapBridgeSession,
  bridgeClaimQuest,
  bridgeTickSession,
  createBridgeSnapshot,
  type TamaBridgeBootstrapInput,
  type TamaBridgeSnapshot,
} from "./bridge";
import { pruneNotifications, pruneSessionEvents } from "./pruning";
import { getSessionEvents, type TamaSessionState } from "./session";
import {
  resolveRuntimeConfig,
  type TamaResolvedRuntimeConfig,
  type TamaRuntimeBootstrapConfigFile,
} from "./runtime-config";
import {
  createWorldStateFromInput,
  tickWorld,
  type TamaWorldBootstrapInput,
  type WorldState,
} from "./world";

export interface TamaLiveLoopState {
  session: TamaSessionState;
  world: WorldState;
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
): { session: TamaSessionState; removedCount: number } {
  const before = getSessionEvents(session).length;

  pruneSessionEvents(session, limit, now);

  const after = getSessionEvents(session).length;

  return {
    session,
    removedCount: Math.max(0, before - after),
  };
}

function enforceNotificationLimit(
  session: TamaSessionState,
  limit: number,
  now: number,
): TamaSessionState {
  pruneNotifications(session, limit, now);
  return session;
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
  input?: TamaBridgeBootstrapInput &
    TamaRuntimeBootstrapConfigFile & {
      world?: TamaWorldBootstrapInput;
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

  let session = boot.session;

  session = enforceNotificationLimit(
    session,
    resolved.config.loop.notificationLimit,
    now,
  );

  session = enforceEventLimit(
    session,
    resolved.config.loop.eventQueueLimit,
    now,
  ).session;

  return {
    session,
    world: createWorldStateFromInput(input?.world),
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

  session = enforceNotificationLimit(
    session,
    input.config.loop.notificationLimit,
    now,
  );

  const pruned = enforceEventLimit(
    session,
    input.config.loop.eventQueueLimit,
    now,
  );

  session = pruned.session;

  const world: WorldState = {
    clock: {
      ...input.world.clock,
    },
    zone: input.world.zone,
    weather: input.world.weather,
    flags: {
      ...input.world.flags,
    },
  };

  tickWorld(world);

  const state: TamaLiveLoopState = {
    ...input,
    session,
    world,
    updatedAt: now,
    tickCount: input.tickCount + 1,
  };

  return {
    state,
    snapshot: createBridgeSnapshot(session),
    consumedEventCount: pruned.removedCount,
    claimedQuestIds: autoClaim.claimedQuestIds,
  };
}
