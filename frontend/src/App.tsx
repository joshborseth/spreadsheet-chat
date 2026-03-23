import { Conversation } from "./components/Conversation";
import { QuestionPanel } from "./components/QuestionPanel";
import { UploadPanel } from "./components/UploadPanel";
import { useSpreadsheetChat } from "./hooks/useSpreadsheetChat";

export default function App() {
  const {
    fileId,
    uploadInfo,
    uploadError,
    messages,
    input,
    setInput,
    busy,
    onFile,
    send,
  } = useSpreadsheetChat();

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <UploadPanel
          onFile={onFile}
          uploadError={uploadError}
          uploadInfo={uploadInfo}
        />
      </aside>
      <main className="app-main">
        <div className="app-chat-column">
          <header className="chat-header">
            <h1>Spreadsheet Q&amp;A</h1>
            <p className="sub">
              Upload an .xlsx, ask questions in plain language.
            </p>
          </header>
          <Conversation messages={messages} />
          <QuestionPanel
            fileId={fileId}
            input={input}
            setInput={setInput}
            busy={busy}
            send={send}
          />
        </div>
      </main>
    </div>
  );
}
