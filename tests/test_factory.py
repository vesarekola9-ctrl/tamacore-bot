import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from tamacore.factory_v3_1.generator import build_game_json
from tamacore.factory_v3_1.realtime_runtime import apply_realtime_runtime
from tamacore.factory_v3_1.evolution_runtime import apply_evolution_runtime

@pytest.fixture
def base_data():
    return {
        "properties": {"name": "Test Game"},
        "layouts": [{"name": "MainScene", "objects": [], "events": []}],
        "globalVariables": []
    }

def test_build_game_json(base_data):
    res = build_game_json(base_data)
    assert "globalVariables" in res
    var_names = {v["name"] for v in res["globalVariables"]}
    assert "RealTime_LastTickTimestamp" in var_names
    assert "Pet_GrowthStage" in var_names
    assert "Quest_FeedCount" in var_names
    assert "Audio_MusicVolume" in var_names
    assert "Ach_FirstFeed_Unlocked" in var_names

def test_realtime_events(base_data):
    res = apply_realtime_runtime(base_data)
    layout = res["layouts"][0]
    assert len(layout["events"]) > 0

def test_evolution_events(base_data):
    res = apply_evolution_runtime(base_data)
    layout = res["layouts"][0]
    assert len(layout["events"]) > 0
