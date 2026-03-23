import { useCallback, useState } from "react";

import { postChat, uploadWorkbook } from "../api/spreadsheet";
import type {
  ChatMessage,
  ChatResponse,
  UploadResponse,
} from "../schemas/spreadsheet";

function assistantErrorPayload(message: string): ChatResponse {
  return {
    reply_text: "",
    generated_code: "",
    sources: [],
    warnings: [],
    error: message,
    traceback: null,
  };
}

export function useSpreadsheetChat() {
  const [fileId, setFileId] = useState<string | null>(null);
  const [uploadInfo, setUploadInfo] = useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const onFile = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setUploadError(null);
    setFileId(null);
    setUploadInfo(null);
    setMessages([]);
    try {
      const data = await uploadWorkbook(f);
      setFileId(data.file_id);
      setUploadInfo(data);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    }
  }, []);

  const send = useCallback(async () => {
    const q = input.trim();
    if (!fileId || !q || busy) return;
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", text: q }]);
    try {
      const data = await postChat(fileId, q);
      setMessages((m) => [...m, { role: "assistant", payload: data }]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          payload: assistantErrorPayload(
            err instanceof Error ? err.message : "Request failed",
          ),
        },
      ]);
    } finally {
      setBusy(false);
    }
  }, [fileId, input, busy]);

  return {
    fileId,
    uploadInfo,
    uploadError,
    messages,
    input,
    setInput,
    busy,
    onFile,
    send,
  };
}
