class WorldSystem {
    constructor(runtime) {
        this.runtime = runtime
        this.lastTick = 0
        this.tickInterval = 1000
    }

    update(now) {
        if (now - this.lastTick < this.tickInterval) return
        this.lastTick = now

        const state = this.runtime.state
        if (!state) return

        if (!state.world) {
            state.world = {
                clock: { day: 1, time: 0, speed: 1 },
                zone: "home",
                weather: "clear",
                flags: {}
            }
        }

        this.tickClock(state)
        this.tickNeeds(state)
    }

    tickClock(state) {
        const clock = state.world.clock

        clock.time += clock.speed

        if (clock.time >= 1440) {
            clock.time = 0
            clock.day += 1

            this.runtime.dispatch("WORLD_NEW_DAY", {
                day: clock.day
            })
        }
    }

    tickNeeds(state) {

        if (state.hunger != null)
            state.hunger = Math.min(100, state.hunger + 1)

        if (state.energy != null)
            state.energy = Math.max(0, state.energy - 1)

        if (state.happiness != null && state.hunger > 80)
            state.happiness = Math.max(0, state.happiness - 1)

        if (state.health != null && state.hunger >= 100)
            state.health = Math.max(0, state.health - 1)
    }

    setZone(zone) {
        const state = this.runtime.state
        if (!state.world) return

        state.world.zone = zone

        this.runtime.dispatch("WORLD_ZONE_CHANGED", {
            zone
        })
    }

    setWeather(weather) {
        const state = this.runtime.state
        if (!state.world) return

        state.world.weather = weather

        this.runtime.dispatch("WORLD_WEATHER_CHANGED", {
            weather
        })
    }
}

module.exports = WorldSystem
