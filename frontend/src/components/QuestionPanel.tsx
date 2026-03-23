type Props = {
  fileId: string | null
  input: string
  setInput: (v: string) => void
  busy: boolean
  send: () => void | Promise<void>
}

export function QuestionPanel({
  fileId,
  input,
  setInput,
  busy,
  send,
}: Props) {
  return (
    <div className="composer">
      <label htmlFor="q" className="visually-hidden">
        Question
      </label>
      <div className="chat-form">
        <textarea
          id="q"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            fileId
              ? 'e.g. What is the total sales in Q1?'
              : 'Upload a file first…'
          }
          disabled={!fileId || busy}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              e.preventDefault()
              void send()
            }
          }}
        />
        <button
          type="button"
          className="primary"
          disabled={!fileId || !input.trim() || busy}
          onClick={() => void send()}
        >
          {busy ? '…' : 'Ask'}
        </button>
      </div>
      <p className="composer-tip">
        <kbd>Cmd/Ctrl</kbd> + <kbd>Enter</kbd> to send
      </p>
    </div>
  )
}
