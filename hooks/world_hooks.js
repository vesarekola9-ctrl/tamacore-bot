module.exports = function(runtime) {

    runtime.on("WORLD_SET_ZONE", data => {

        if (!runtime.loop) return
        if (!runtime.loop.world) return

        runtime.loop.world.setZone(data.zone)

    })

    runtime.on("WORLD_SET_WEATHER", data => {

        if (!runtime.loop) return
        if (!runtime.loop.world) return

        runtime.loop.world.setWeather(data.weather)

    })

}
