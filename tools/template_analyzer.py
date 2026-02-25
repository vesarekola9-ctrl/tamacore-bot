from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

ROOT = Path(".")
TEMPLATE_DIR = Path("input") / "template_project"

OUT_REPORTS = Path("output") / "reports"
OUT_SCAFFOLD = Path("output") / "scaffold"

MAPPING_JSON = Path("output") / "assets_raw" / "mapping.json"


def read_json_safe(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def find_candidate_json_files(base: Path):
    files = [p for p in base.rglob("*.json") if p.is_file()]
    files.sort(key=lambda x: x.stat().st_size, reverse=True)
    return files


def looks_like_gdevelop_project(obj) -> bool:
    if not isinstance(obj, dict):
        return False
    s = json.dumps(obj, ensure_ascii=False)[:2000].lower()
    return ("gdevelop" in s) or ("gdjs" in s) or ("layouts" in s) or ("objects" in s and "resources" in s)


def extract_strings(obj, out: list[str], limit: int = 25000):
    if len(out) >= limit:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str):
                out.append(k)
            extract_strings(v, out, limit)
    elif isinstance(obj, list):
        for v in obj:
            extract_strings(v, out, limit)
    elif isinstance(obj, str):
        out.append(obj)


def infer_naming_conventions(strings: list[str]):
    stats = {
        "snake_case": 0,
        "kebab_case": 0,
        "camel_case": 0,
        "has_double_underscore": 0,
        "has_version_tag": 0,
        "common_prefixes": [],
        "common_suffixes": [],
    }

    prefixes = Counter()
    suffixes = Counter()
    version_re = re.compile(r"__v\d{3}\b", re.IGNORECASE)

    for s in strings:
        if not isinstance(s, str):
            continue
        if len(s) < 3 or len(s) > 80:
            continue

        if "__" in s:
            stats["has_double_underscore"] += 1
        if version_re.search(s):
            stats["has_version_tag"] += 1

        if re.fullmatch(r"[a-z0-9_]+", s):
            stats["snake_case"] += 1
        if re.fullmatch(r"[a-z0-9\-]+", s):
            stats["kebab_case"] += 1
        if re.fullmatch(r"[A-Z][A-Za-z0-9]+(?:[A-Z][A-Za-z0-9]+)+", s):
            stats["camel_case"] += 1

        tok = re.split(r"__|_|-", s)
        tok = [t for t in tok if t]
        if len(tok) >= 2:
            prefixes[tok[0].lower()] += 1
            suffixes[tok[-1].lower()] += 1

    stats["common_prefixes"] = prefixes.most_common(15)
    stats["common_suffixes"] = suffixes.most_common(15)
    return stats


def analyze_template_project():
    result = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "template_dir": str(TEMPLATE_DIR),
        "exists": TEMPLATE_DIR.exists(),
        "file_counts": {},
        "candidate_project_jsons": [],
        "selected_project_json": None,
        "naming_inference": {},
        "scene_names_guess": [],
        "object_names_guess": [],
    }

    if not TEMPLATE_DIR.exists():
        return result

    ext_counts = Counter()
    for p in TEMPLATE_DIR.rglob("*"):
        if p.is_file():
            ext_counts[p.suffix.lower()] += 1
    result["file_counts"] = dict(ext_counts)

    candidates = find_candidate_json_files(TEMPLATE_DIR)
    selected = None

    for p in candidates[:50]:
        obj = read_json_safe(p)
        if obj is None:
            continue
        is_gd = looks_like_gdevelop_project(obj)
        result["candidate_project_jsons"].append(
            {"path": str(p), "bytes": p.stat().st_size, "looks_like_gdevelop": is_gd}
        )
        if is_gd and selected is None:
            selected = p

    if selected:
        result["selected_project_json"] = str(selected)
        obj = read_json_safe(selected)
        strings: list[str] = []
        extract_strings(obj, strings)

        result["naming_inference"] = infer_naming_conventions(strings)

        scene_like = Counter()
        obj_like = Counter()
        for s in strings:
            if not isinstance(s, str):
                continue
            sl = s.lower()
            if len(sl) < 3 or len(sl) > 60:
                continue
            if any(k in sl for k in ["home", "shop", "inventory", "inv", "menu", "hud", "ui"]):
                scene_like[s] += 1
            if any(k in sl for k in ["btn", "button", "pet", "slot", "icon", "txt"]):
                obj_like[s] += 1

        result["scene_names_guess"] = [k for k, _ in scene_like.most_common(30)]
        result["object_names_guess"] = [k for k, _ in obj_like.most_common(40)]

    return result


def analyze_mapping():
    m = read_json_safe(MAPPING_JSON)
    if not isinstance(m, dict):
        return {"exists": False, "path": str(MAPPING_JSON)}

    items = m.get("items", [])
    cats = Counter()
    names = []
    for it in items:
        try:
            cats[str(it.get("category", "_")).lower()] += 1
            src = str(it.get("source", ""))
            names.append(Path(src).name.lower())
        except Exception:
            pass

    slot = Counter()
    for n in names:
        if any(x in n for x in ["hat", "cap", "beanie"]):
            slot["hat"] += 1
        elif any(x in n for x in ["glass", "glasses", "shade"]):
            slot["glasses"] += 1
        elif any(x in n for x in ["skin", "outfit", "body"]):
            slot["skin"] += 1
        else:
            slot["misc"] += 1

    return {
        "exists": True,
        "path": str(MAPPING_JSON),
        "summary": m.get("summary", {}),
        "category_counts": dict(cats),
        "slot_guess_counts": dict(slot),
    }


def main():
    OUT_REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_SCAFFOLD.mkdir(parents=True, exist_ok=True)

    tpl = analyze_template_project()
    mapping = analyze_mapping()

    report = {
        "template": tpl,
        "assets_mapping": mapping,
        "recommendations": {
            "next_step": "Use template_conventions.json to drive scene/object naming + UI layout generation.",
            "template_dir_hint": "Put your reference GDevelop project into input/template_project/ (any structure).",
        },
    }

    (OUT_REPORTS / "template_analysis.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    conventions = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "naming": tpl.get("naming_inference", {}),
        "scene_name_suggestions": tpl.get("scene_names_guess", []),
        "object_name_suggestions": tpl.get("object_names_guess", []),
        "assets": mapping,
    }

    (OUT_SCAFFOLD / "template_conventions.json").write_text(
        json.dumps(conventions, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("[✓] Template Analyzer done")
    print(" - output/reports/template_analysis.json")
    print(" - output/scaffold/template_conventions.json")


if __name__ == "__main__":
    main()
