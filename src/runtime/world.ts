export type WorldClock = {
  day: number
  time: number
  speed: number
}

export type WorldFlags = {
  isNight: boolean
  isMorning: boolean
  isEvening: boolean
}

export type WorldState = {
  clock: WorldClock
  zone: string
  weather: string
  flags: WorldFlags
}

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
  }
}

export function tickWorld(world: WorldState) {
  world.clock.time += world.clock.speed

  if (world.clock.time >= 1440) {
    world.clock.time = 0
    world.clock.day += 1
  }

  const hour = Math.floor(world.clock.time / 60)

  world.flags.isNight = hour >= 20 || hour < 6
  world.flags.isMorning = hour >= 6 && hour < 12
  world.flags.isEvening = hour >= 17 && hour < 20
}

export function setZone(world: WorldState, zone: string) {
  world.zone = zone
}

export function setWeather(world: WorldState, weather: string) {
  world.weather = weather
}
