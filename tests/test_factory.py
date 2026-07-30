import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import pytest
from tamacore.factory_v3_1.generator import build_game_json

@pytest.fixture
def base_data():
    return {
        "properties": {"name": "Test Game"},
        "layouts": [{"name": "MainScene", "objects": [], "instances": [], "events": []}],
        "globalVariables": [],
        "resources": {"resources": []}
    }

def test_build_game_json(base_data):
    res = build_game_json(base_data)
    assert "globalVariables" in res
    var_names = {v["name"] for v in res["globalVariables"]}
    assert "Pet_CurrentEmote" in var_names
    assert "Seasonal_ActiveEvent" in var_names
