import type { ChatMessage, ChatResponse } from "../schemas/spreadsheet";

type Props = {
  messages: ChatMessage[];
};

function AssistantMessage({ payload }: { payload: ChatResponse }) {
  return (
    <div className={`msg assistant${payload.error ? " error" : ""}`}>
      {payload.error && (
        <div>
          <strong>Error:</strong> {payload.error}
        </div>
      )}
      {payload.reply_text && <div>{payload.reply_text}</div>}
      {payload.reasoning_brief && (
        <div className="sources" style={{ marginTop: "0.35rem" }}>
          {payload.reasoning_brief}
        </div>
      )}
      {payload.sources.length > 0 && (
        <div className="sources">
          <strong>Sources</strong>
          <ul>
            {payload.sources.map((s, j) => (
              <li key={j}>
                <strong>{s.sheet_name}</strong>
                {s.cells_or_range ? ` · ${s.cells_or_range}` : ""}
                {s.note ? ` — ${s.note}` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
      {payload.warnings.length > 0 && (
        <div className="warnings">{payload.warnings.join(" ")}</div>
      )}
      {payload.traceback && (
        <details className="code-block">
          <summary>Traceback</summary>
          <pre>{payload.traceback}</pre>
        </details>
      )}
      {payload.generated_code && (
        <details className="code-block">
          <summary>Generated Python</summary>
          <pre>{payload.generated_code}</pre>
        </details>
      )}
    </div>
  );
}

export function Conversation({ messages }: Props) {
  return (
    <div
      className="conversation-scroll"
      role="log"
      aria-label="Conversation"
      aria-live="polite"
    >
      <div className="messages">
        {Boolean(messages.length) &&
          messages.map((msg, i) =>
            msg.role === "user" ? (
              <div key={i} className="msg user">
                {msg.text}
              </div>
            ) : (
              <AssistantMessage key={i} payload={msg.payload} />
            ),
          )}
      </div>
    </div>
  );
}
