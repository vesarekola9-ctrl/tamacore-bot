from dataclasses import dataclass, field


@dataclass
class WorldClock:
    day: int = 1
    time: int = 0
    speed: int = 1


@dataclass
class WorldFlags:
    isNight: bool = False
    isMorning: bool = False
    isEvening: bool = False


@dataclass
class WorldState:
    clock: WorldClock = field(default_factory=WorldClock)
    zone: str = "home"
    weather: str = "clear"
    flags: WorldFlags = field(default_factory=WorldFlags)


class WorldSystem:

    def __init__(self):
        self.world = WorldState()

    def tick(self):

        self.world.clock.time += self.world.clock.speed

        if self.world.clock.time >= 1440:
            self.world.clock.time = 0
            self.world.clock.day += 1

        self._update_flags()

    def _update_flags(self):

        hour = int(self.world.clock.time / 60)

        self.world.flags.isNight = hour >= 20 or hour < 6
        self.world.flags.isMorning = 6 <= hour < 12
        self.world.flags.isEvening = 17 <= hour < 20

    def set_zone(self, zone: str):
        self.world.zone = zone

    def set_weather(self, weather: str):
        self.world.weather = weather

    def export(self):
        return {
            "world": {
                "day": self.world.clock.day,
                "time": self.world.clock.time,
                "zone": self.world.zone,
                "weather": self.world.weather,
                "flags": {
                    "night": self.world.flags.isNight,
                    "morning": self.world.flags.isMorning,
                    "evening": self.world.flags.isEvening,
                },
            }
        }
