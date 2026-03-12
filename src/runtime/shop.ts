import {
  getCatalogItem,
  type TamaCatalogItem,
  type TamaCatalogLike,
} from "./catalog";
import { addItem } from "./inventory";

export interface TamaWalletLike {
  coins?: number;
  updatedAt?: number;
  [key: string]: unknown;
}

export interface TamaShopPurchaseResult {
  success: boolean;
  reason?: "ITEM_NOT_FOUND" | "ITEM_HAS_NO_PRICE" | "NOT_ENOUGH_COINS";
  item?: TamaCatalogItem;
  paidCoins?: number;
  remainingCoins?: number;
}

function readCoins(target: TamaWalletLike): number {
  return typeof target.coins === "number" && Number.isFinite(target.coins)
    ? Math.max(0, Math.floor(target.coins))
    : 0;
}

function writeCoins(target: TamaWalletLike, value: number, now: number): number {
  const next = Math.max(0, Math.floor(value));
  target.coins = next;
  target.updatedAt = now;
  return next;
}

export function getCoins(target: TamaWalletLike): number {
  return readCoins(target);
}

export function grantCoins(
  target: TamaWalletLike,
  amount: number,
  now = Date.now(),
): number {
  const safeAmount =
    typeof amount === "number" && Number.isFinite(amount) ? Math.floor(amount) : 0;

  return writeCoins(target, readCoins(target) + Math.max(0, safeAmount), now);
}

export function spendCoins(
  target: TamaWalletLike,
  amount: number,
  now = Date.now(),
): boolean {
  const safeAmount =
    typeof amount === "number" && Number.isFinite(amount) ? Math.max(0, Math.floor(amount)) : 0;

  if (readCoins(target) < safeAmount) return false;
  writeCoins(target, readCoins(target) - safeAmount, now);
  return true;
}

export function buyCatalogItem(
  target: TamaWalletLike & TamaCatalogLike & { inventory?: { itemId: string; quantity: number }[] },
  itemId: string,
  now = Date.now(),
): TamaShopPurchaseResult {
  const item = getCatalogItem(target, itemId);

  if (!item) {
    return {
      success: false,
      reason: "ITEM_NOT_FOUND",
    };
  }

  if (typeof item.price !== "number" || !Number.isFinite(item.price)) {
    return {
      success: false,
      reason: "ITEM_HAS_NO_PRICE",
      item,
    };
  }

  const price = Math.max(0, Math.floor(item.price));

  if (readCoins(target) < price) {
    return {
      success: false,
      reason: "NOT_ENOUGH_COINS",
      item,
      remainingCoins: readCoins(target),
    };
  }

  spendCoins(target, price, now);
  addItem(target, item.id, 1, now);

  return {
    success: true,
    item,
    paidCoins: price,
    remainingCoins: readCoins(target),
  };
}
