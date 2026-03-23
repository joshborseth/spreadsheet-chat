import type { UploadResponse } from "../schemas/spreadsheet";

type Props = {
  onFile: (e: React.ChangeEvent<HTMLInputElement>) => void;
  uploadError: string | null;
  uploadInfo: UploadResponse | null;
};

export function UploadPanel({ onFile, uploadError, uploadInfo }: Props) {
  return (
    <div className="panel">
      <h2 className="sidebar-heading">Workbook</h2>
      <label htmlFor="xlsx" className="visually-hidden">
        Choose .xlsx file
      </label>
      <input
        id="xlsx"
        type="file"
        accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        onChange={onFile}
      />
      {uploadError && <p className="warnings">{uploadError}</p>}
      {uploadInfo && (
        <div className="sheet-list">
          <strong>{uploadInfo.filename}</strong> —{" "}
          {(uploadInfo.bytes_approx / 1024).toFixed(1)} KB
          <div>Sheets: {uploadInfo.sheets.join(", ")}</div>
        </div>
      )}
    </div>
  );
}
