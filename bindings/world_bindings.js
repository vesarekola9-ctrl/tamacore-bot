function get(state, path, def = 0) {

    const parts = path.split(".")

    let cur = state

    for (const p of parts) {

        if (cur == null) return def
        cur = cur[p]

    }

    return cur ?? def
}

module.exports = {

    bindWorld(scene, runtime) {

        scene.getDay = () =>
            get(runtime.state, "world.clock.day", 1)

        scene.getTime = () =>
            get(runtime.state, "world.clock.time", 0)

        scene.getZone = () =>
            get(runtime.state, "world.zone", "home")

        scene.getWeather = () =>
            get(runtime.state, "world.weather", "clear")

    }

}
