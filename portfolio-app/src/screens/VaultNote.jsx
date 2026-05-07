import { useEffect, useState } from "react";
import { Filesystem, Directory, Encoding } from "@capacitor/filesystem";
import { marked } from "marked";
import "./VaultNote.css";

const BackIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="m15 18-6-6 6-6" />
  </svg>
);

function processObsidian(md) {
  return md
    .replace(/^---[\s\S]*?^---\s*/m, "")         // strip YAML frontmatter
    .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2") // [[path|alias]] → alias
    .replace(/\[\[([^\]]+)\]\]/g, "$1");            // [[link]] → plain text
}

marked.setOptions({ breaks: true, gfm: true });

export default function VaultNote({ note, onBack }) {
  const [html, setHtml] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const title = note.name.replace(/\.md$/, "");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError("");
      try {
        const result = await Filesystem.readFile({
          path: note.path,
          directory: Directory.ExternalStorage,
          encoding: Encoding.UTF8,
        });
        const processed = processObsidian(result.data);
        setHtml(marked.parse(processed));
      } catch (e) {
        setError(e.message || "Failed to read note");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [note.path]);

  return (
    <div className="screen vault-note-screen">
      <header className="vault-note-nav">
        <button className="back-btn" onClick={onBack} aria-label="Back to vault">
          <BackIcon />
          <span>Vault</span>
        </button>
        <span className="vault-note-nav-title" title={title}>{title}</span>
      </header>

      <div className="scroll-body vault-note-body">
        {loading && <div className="vault-spinner" aria-label="Loading" role="status" />}
        {error  && <p className="vault-note-error">⚠️ {error}</p>}
        {!loading && !error && (
          <article
            className="vault-md-body"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        )}
        <div className="list-pad" />
      </div>
    </div>
  );
}
