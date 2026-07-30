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
    assert "Audio_SFXVolume" in var_names
    assert "Cosmetic_EquippedHat" in var_names
    
    # Verify Overlay Objects present in Layout
    objects = res["layouts"][0]["objects"]
    obj_names = {o["name"] for o in objects}
    assert "Pet_HatObject" in obj_names
    assert "Pet_OutfitObject" in obj_names
