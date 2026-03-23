import { z } from "zod";

import {
  chatResponseSchema,
  type ChatResponse,
  type UploadResponse,
  uploadResponseSchema,
} from "../schemas/spreadsheet";

export function parseFastApiErrorBody(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const d = (body as { detail?: unknown }).detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => JSON.stringify(x)).join("; ");
  return fallback;
}

function parseWithSchema<T>(
  schema: z.ZodType<T>,
  data: unknown,
  label: string,
): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    throw new Error(`${label}: ${result.error.message}`);
  }
  return result.data;
}

export async function uploadWorkbook(file: File): Promise<UploadResponse> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/api/upload", { method: "POST", body: fd });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(parseFastApiErrorBody(body, res.statusText));
  }
  return parseWithSchema(uploadResponseSchema, body, "Upload response");
}

export async function postChat(
  fileId: string,
  message: string,
): Promise<ChatResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ file_id: fileId, message }),
  });
  const body = await res.json();
  if (!res.ok) {
    throw new Error(parseFastApiErrorBody(body, res.statusText));
  }
  return parseWithSchema(chatResponseSchema, body, "Chat response");
}
