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

export function createWorldState(): WorldState {
  return {
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
}

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

export function tickWorld(world: WorldState): WorldState {
  const previousTime = normalizeWorldTime(world.clock.time);

  world.clock.time = normalizeWorldTime(previousTime + world.clock.speed);

  if (world.clock.time < previousTime) {
    world.clock.day += 1;
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
