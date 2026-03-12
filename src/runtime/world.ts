export type WorldClock = {
  day: number;
  time: number;
  speed: number;
};

export type WorldFlags = {
  isNight: boolean;
  isMorning: boolean;
  isEvening: boolean;
};

export type WorldState = {
  clock: WorldClock;
  zone: string;
  weather: string;
  flags: WorldFlags;
};

export type TamaWorldBootstrapInput = Partial<WorldState> & {
  clock?: Partial<WorldClock>;
  flags?: Partial<WorldFlags>;
};

export function normalizeWorldTime(time: number): number {
  if (!Number.isFinite(time)) return 0;

  const normalized = Math.floor(time) % 1440;
  return normalized < 0 ? normalized + 1440 : normalized;
}

export function updateWorldFlags(world: WorldState): WorldState {
  const hour = Math.floor(normalizeWorldTime(world.clock.time) / 60);

  world.flags.isNight = hour >= 20 || hour < 6;
  world.flags.isMorning = hour >= 6 && hour < 12;
  world.flags.isEvening = hour >= 17 && hour < 20;

  return world;
}

export function createWorldState(): WorldState {
  const world: WorldState = {
    clock: {
      day: 1,
      time: 0,
      speed: 1,
    },
    zone: "home",
    weather: "clear",
    flags: {
      isNight: false,
      isMorning: false,
      isEvening: false,
    },
  };

  return updateWorldFlags(world);
}

export function tickWorld(world: WorldState): WorldState {
  const previousTime = normalizeWorldTime(world.clock.time);
  const speed = Number.isFinite(world.clock.speed) ? world.clock.speed : 1;
  const nextRawTime = previousTime + speed;

  world.clock.time = normalizeWorldTime(nextRawTime);

  if (world.clock.time < previousTime || nextRawTime >= 1440) {
    world.clock.day = Math.max(1, Math.floor(world.clock.day) + 1);
  }

  return updateWorldFlags(world);
}

export function setZone(world: WorldState, zone: string): WorldState {
  if (typeof zone === "string" && zone.trim()) {
    world.zone = zone.trim();
  }

  return world;
}

export function setWeather(world: WorldState, weather: string): WorldState {
  if (typeof weather === "string" && weather.trim()) {
    world.weather = weather.trim();
  }

  return world;
}

export function cloneWorldState(world: WorldState): WorldState {
  return {
    clock: {
      day: world.clock.day,
      time: world.clock.time,
      speed: world.clock.speed,
    },
    zone: world.zone,
    weather: world.weather,
    flags: {
      isNight: world.flags.isNight,
      isMorning: world.flags.isMorning,
      isEvening: world.flags.isEvening,
    },
  };
}

export function createWorldStateFromInput(
  input?: TamaWorldBootstrapInput,
): WorldState {
  const world = createWorldState();

  if (!input) {
    return world;
  }

  if (typeof input.zone === "string" && input.zone.trim()) {
    world.zone = input.zone.trim();
  }

  if (typeof input.weather === "string" && input.weather.trim()) {
    world.weather = input.weather.trim();
  }

  if (input.clock) {
    if (typeof input.clock.day === "number" && Number.isFinite(input.clock.day)) {
      world.clock.day = Math.max(1, Math.floor(input.clock.day));
    }

    if (typeof input.clock.time === "number" && Number.isFinite(input.clock.time)) {
      world.clock.time = normalizeWorldTime(input.clock.time);
    }

    if (typeof input.clock.speed === "number" && Number.isFinite(input.clock.speed)) {
      world.clock.speed = input.clock.speed;
    }
  }

  if (input.flags) {
    if (typeof input.flags.isNight === "boolean") {
      world.flags.isNight = input.flags.isNight;
    }

    if (typeof input.flags.isMorning === "boolean") {
      world.flags.isMorning = input.flags.isMorning;
    }

    if (typeof input.flags.isEvening === "boolean") {
      world.flags.isEvening = input.flags.isEvening;
    }
  }

  return updateWorldFlags(world);
}
