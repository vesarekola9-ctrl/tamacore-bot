export interface TamaInventoryEntry {
  itemId: string;
  quantity: number;
}

export interface TamaInventoryLike {
  inventory?: TamaInventoryEntry[];
  updatedAt?: number;
  [key: string]: unknown;
}

export interface TamaInventoryChangeResult {
  inventory: TamaInventoryEntry[];
  itemId: string;
  quantity: number;
  nextQuantity: number;
  changed: boolean;
}

function ensureInventory(target: TamaInventoryLike): TamaInventoryEntry[] {
  if (!Array.isArray(target.inventory)) {
    target.inventory = [];
  }

  target.inventory = target.inventory
    .filter(
      (entry) =>
        !!entry &&
        typeof entry.itemId === "string" &&
        entry.itemId.length > 0 &&
        typeof entry.quantity === "number" &&
        Number.isFinite(entry.quantity) &&
        entry.quantity > 0,
    )
    .map((entry) => ({
      itemId: entry.itemId,
      quantity: Math.floor(entry.quantity),
    }));

  return target.inventory;
}

function findEntryIndex(inventory: TamaInventoryEntry[], itemId: string): number {
  return inventory.findIndex((entry) => entry.itemId === itemId);
}

function cloneInventory(inventory: TamaInventoryEntry[]): TamaInventoryEntry[] {
  return inventory.map((entry) => ({
    itemId: entry.itemId,
    quantity: entry.quantity,
  }));
}

export function getItemQuantity(target: TamaInventoryLike, itemId: string): number {
  const inventory = ensureInventory(target);
  const index = findEntryIndex(inventory, itemId);
  return index >= 0 ? inventory[index].quantity : 0;
}

export function hasItem(
  target: TamaInventoryLike,
  itemId: string,
  minQuantity = 1,
): boolean {
  return getItemQuantity(target, itemId) >= Math.max(1, Math.floor(minQuantity));
}

export function addItem(
  target: TamaInventoryLike,
  itemId: string,
  quantity = 1,
  now = Date.now(),
): TamaInventoryChangeResult {
  const inventory = cloneInventory(ensureInventory(target));
  const safeQuantity = Math.max(0, Math.floor(quantity));
  const index = findEntryIndex(inventory, itemId);

  if (safeQuantity <= 0) {
    return {
      inventory,
      itemId,
      quantity: 0,
      nextQuantity: index >= 0 ? inventory[index].quantity : 0,
      changed: false,
    };
  }

  if (index >= 0) {
    inventory[index] = {
      ...inventory[index],
      quantity: inventory[index].quantity + safeQuantity,
    };
  } else {
    inventory.push({
      itemId,
      quantity: safeQuantity,
    });
  }

  target.inventory = inventory;
  target.updatedAt = now;

  return {
    inventory,
    itemId,
    quantity: safeQuantity,
    nextQuantity: getItemQuantity(target, itemId),
    changed: true,
  };
}

export function removeItem(
  target: TamaInventoryLike,
  itemId: string,
  quantity = 1,
  now = Date.now(),
): TamaInventoryChangeResult {
  const inventory = cloneInventory(ensureInventory(target));
  const safeQuantity = Math.max(0, Math.floor(quantity));
  const index = findEntryIndex(inventory, itemId);

  if (safeQuantity <= 0 || index < 0) {
    return {
      inventory,
      itemId,
      quantity: 0,
      nextQuantity: index >= 0 ? inventory[index].quantity : 0,
      changed: false,
    };
  }

  const current = inventory[index].quantity;
  const nextQuantity = Math.max(0, current - safeQuantity);

  if (nextQuantity <= 0) {
    inventory.splice(index, 1);
  } else {
    inventory[index] = {
      ...inventory[index],
      quantity: nextQuantity,
    };
  }

  target.inventory = inventory;
  target.updatedAt = now;

  return {
    inventory,
    itemId,
    quantity: safeQuantity,
    nextQuantity: getItemQuantity(target, itemId),
    changed: true,
  };
}

export function setItemQuantity(
  target: TamaInventoryLike,
  itemId: string,
  quantity: number,
  now = Date.now(),
): TamaInventoryChangeResult {
  const inventory = cloneInventory(ensureInventory(target));
  const safeQuantity = Math.max(0, Math.floor(quantity));
  const index = findEntryIndex(inventory, itemId);

  if (safeQuantity <= 0) {
    if (index >= 0) inventory.splice(index, 1);
  } else if (index >= 0) {
    inventory[index] = {
      ...inventory[index],
      quantity: safeQuantity,
    };
  } else {
    inventory.push({
      itemId,
      quantity: safeQuantity,
    });
  }

  target.inventory = inventory;
  target.updatedAt = now;

  return {
    inventory,
    itemId,
    quantity: safeQuantity,
    nextQuantity: getItemQuantity(target, itemId),
    changed: true,
  };
}

export function listInventory(target: TamaInventoryLike): TamaInventoryEntry[] {
  return cloneInventory(ensureInventory(target));
}
