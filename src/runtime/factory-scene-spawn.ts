import type { TamaLiveLoopState } from "./live-loop";
import type { TamaCatalogItem } from "./catalog";

export type FactorySpawnObject = {
  id: string;
  x: number;
  y: number;
  layer: string;
  visible: boolean;
};

export type FactorySceneState = {
  objects: FactorySpawnObject[];
};

function safeNumber(v: unknown, def = 0): number {
  return typeof v === "number" && Number.isFinite(v) ? v : def;
}

function safeString(v: unknown, def = ""): string {
  return typeof v === "string" ? v : def;
}

function buildItemObject(
  item: TamaCatalogItem,
  index: number,
): FactorySpawnObject {
  const baseX = 100;
  const baseY = 100;

  const spacing = 80;

  return {
    id: item.id,
    x: baseX + index * spacing,
    y: baseY,
    layer: "Items",
    visible: true,
  };
}

function buildPetObject(): FactorySpawnObject {
  return {
    id: "pet",
    x: 400,
    y: 300,
    layer: "Pet",
    visible: true,
  };
}

function buildWorldObject(): FactorySpawnObject {
  return {
    id: "world",
    x: 0,
    y: 0,
    layer: "World",
    visible: true,
  };
}

export function buildFactorySceneState(
  liveLoop: TamaLiveLoopState,
): FactorySceneState {
  const objects: FactorySpawnObject[] = [];

  objects.push(buildWorldObject());

  objects.push(buildPetObject());

  const items = liveLoop.session.items;

  for (let i = 0; i < items.length; i++) {
    objects.push(buildItemObject(items[i], i));
  }

  return {
    objects,
  };
}

export function cloneFactorySceneState(
  state: FactorySceneState,
): FactorySceneState {
  return {
    objects: state.objects.map((o) => ({
      id: o.id,
      x: o.x,
      y: o.y,
      layer: o.layer,
      visible: o.visible,
    })),
  };
}

export function applySceneOffset(
  state: FactorySceneState,
  dx: number,
  dy: number,
): FactorySceneState {
  const next = cloneFactorySceneState(state);

  for (const o of next.objects) {
    o.x += dx;
    o.y += dy;
  }

  return next;
}

export function findSceneObject(
  state: FactorySceneState,
  id: string,
): FactorySpawnObject | undefined {
  return state.objects.find((o) => o.id === id);
}

export function setObjectVisible(
  state: FactorySceneState,
  id: string,
  visible: boolean,
): FactorySceneState {
  const next = cloneFactorySceneState(state);

  const obj = next.objects.find((o) => o.id === id);

  if (obj) {
    obj.visible = visible;
  }

  return next;
}

export function moveObject(
  state: FactorySceneState,
  id: string,
  x: number,
  y: number,
): FactorySceneState {
  const next = cloneFactorySceneState(state);

  const obj = next.objects.find((o) => o.id === id);

  if (obj) {
    obj.x = safeNumber(x, obj.x);
    obj.y = safeNumber(y, obj.y);
  }

  return next;
}

export function exportSceneToVariables(
  state: FactorySceneState,
): Record<string, number | string | boolean> {
  const vars: Record<string, number | string | boolean> = {};

  vars["Scene.ObjectCount"] = state.objects.length;

  for (let i = 0; i < state.objects.length; i++) {
    const o = state.objects[i];

    vars[`Scene.${i}.Id`] = safeString(o.id);
    vars[`Scene.${i}.X`] = safeNumber(o.x);
    vars[`Scene.${i}.Y`] = safeNumber(o.y);
    vars[`Scene.${i}.Layer`] = safeString(o.layer);
    vars[`Scene.${i}.Visible`] = o.visible;
  }

  return vars;
}
