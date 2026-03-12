import type { TamaGDevelopCommand } from "./gdevelop-commands";
import type { TamaGDevelopExport } from "./gdevelop-state";

export interface TamaGDevelopSerializedResponse {
  ok: boolean;
  action: string;
  error?: string;
  code?: string;
  result?: Record<string, unknown>;
  gdevelop?: TamaGDevelopExport;
}

function safeParseJson<T>(input: string): T | undefined {
  try {
    return JSON.parse(input) as T;
  } catch {
    return undefined;
  }
}

export function parseGDevelopCommandJson(
  json: string,
): TamaGDevelopCommand | undefined {
  const parsed = safeParseJson<unknown>(json);
  if (!parsed || typeof parsed !== "object") return undefined;
  return parsed as TamaGDevelopCommand;
}

export function parseGDevelopCommandBatchJson(
  json: string,
): TamaGDevelopCommand[] {
  const parsed = safeParseJson<unknown>(json);
  if (!Array.isArray(parsed)) return [];
  return parsed.filter((item) => !!item && typeof item === "object") as TamaGDevelopCommand[];
}

export function serializeGDevelopResponse(
  response: TamaGDevelopSerializedResponse,
): string {
  return JSON.stringify(response);
}

export function serializeGDevelopExport(
  payload: TamaGDevelopExport,
): string {
  return JSON.stringify(payload);
}
