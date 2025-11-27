"use client";
import { useState } from "react";
import { uploadPdf } from "@/lib/api";

export default function UploadForm({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function submit(e) {
    e.preventDefault();
    if (!file) {
      setMessage("Choose a PDF file first.");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const data = await uploadPdf(file);
      setMessage(`✓ ${data.saved_count} questions extracted and saved.`);
      setFile(null);
      onUploaded();
    } catch (err) {
      setMessage("❌ Upload error: " + (err.message || "unknown"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="bg-white p-4 rounded shadow mb-6">
      <h3 className="text-lg font-semibold mb-3">📄 Upload past paper (PDF)</h3>

      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="mb-3 block w-full"
      />

      <div className="flex gap-2">
        <button
          type="submit"
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-60"
          disabled={loading || !file}
        >
          {loading ? "Uploading..." : "Upload & Parse"}
        </button>
        <button
          type="button"
          onClick={() => {
            setFile(null);
            setMessage("");
          }}
          className="px-4 py-2 border rounded hover:bg-gray-100"
        >
          Reset
        </button>
      </div>

      {message && <p className="mt-3 text-sm text-gray-700">{message}</p>}
    </form>
  );
}
