import { z } from "zod";

export const sourceItemSchema = z.object({
  sheet_name: z.string(),
  cells_or_range: z.string(),
  note: z.string(),
});

export const uploadResponseSchema = z.object({
  file_id: z.string(),
  filename: z.string(),
  sheets: z.array(z.string()),
  bytes_approx: z.number(),
});

export const chatResponseSchema = z.object({
  reply_text: z.string(),
  generated_code: z.string(),
  reasoning_brief: z.string().optional(),
  sources: z.array(sourceItemSchema),
  warnings: z.array(z.string()),
  error: z.string().nullable(),
  traceback: z.string().nullable(),
});

export type SourceItem = z.infer<typeof sourceItemSchema>;
export type UploadResponse = z.infer<typeof uploadResponseSchema>;
export type ChatResponse = z.infer<typeof chatResponseSchema>;

export type ChatMessage =
  | { role: "user"; text: string }
  | { role: "assistant"; payload: ChatResponse };
