import { useState, useEffect, useCallback } from "react";
import { Filesystem, Directory } from "@capacitor/filesystem";
import "./VaultScreen.css";

const FolderIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
  </svg>
);

const NoteIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
  </svg>
);

const BackIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="m15 18-6-6 6-6" />
  </svg>
);

const SettingsIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

const VaultBookIcon = () => (
  <svg width="52" height="52" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
    <line x1="12" y1="7" x2="12" y2="13" />
    <line x1="9" y1="10" x2="15" y2="10" />
  </svg>
);

export default function VaultScreen({ onOpenNote }) {
  const [phase, setPhase] = useState("init"); // init | setup | permission | loading | browse | error
  const DEFAULT_VAULT = "Download/vault/Personal Vault";
  const [vaultPath, setVaultPath] = useState(() => localStorage.getItem("vault_path") || DEFAULT_VAULT);
  const [inputPath, setInputPath] = useState(() => localStorage.getItem("vault_path") || DEFAULT_VAULT);
  const [currentPath, setCurrentPath] = useState("");
  const [items, setItems] = useState([]);
  const [errorMsg, setErrorMsg] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  const loadDir = useCallback(async (path) => {
    setPhase("loading");
    setErrorMsg("");
    try {
      const result = await Filesystem.readdir({
        path,
        directory: Directory.ExternalStorage,
      });
      const filtered = result.files
        .filter(f => !f.name.startsWith(".") && (f.type === "directory" || f.name.endsWith(".md")))
        .sort((a, b) => {
          if (a.type === "directory" && b.type !== "directory") return -1;
          if (a.type !== "directory" && b.type === "directory") return 1;
          return a.name.localeCompare(b.name, undefined, { sensitivity: "base" });
        });
      setItems(filtered);
      setCurrentPath(path);
      setPhase("browse");
    } catch (e) {
      const msg = (e.message || "").toLowerCase();
      if (msg.includes("permission") || msg.includes("denied") || msg.includes("access")) {
        setPhase("permission");
      } else if (msg.includes("does not exist") || msg.includes("no such file") || msg.includes("not found")) {
        setPhase("setup");
      } else {
        setErrorMsg(e.message || "Could not read directory");
        setPhase("error");
      }
    }
  }, []);

  useEffect(() => {
    if (!vaultPath) {
      setPhase("setup");
    } else {
      loadDir(vaultPath);
    }
  }, [vaultPath, loadDir]);

  async function requestPermission() {
    try {
      const result = await Filesystem.requestPermissions();
      if (result.publicStorage === "granted") {
        loadDir(vaultPath);
      }
    } catch {
      /* denied — stay on permission screen */
    }
  }

  function saveVaultPath() {
    const trimmed = inputPath.trim().replace(/^\/+|\/+$/g, "");
    if (!trimmed) return;
    localStorage.setItem("vault_path", trimmed);
    setVaultPath(trimmed);
    setShowSettings(false);
  }

  function navigateTo(item) {
    if (item.type === "directory") {
      loadDir(`${currentPath}/${item.name}`);
    } else {
      onOpenNote({ path: `${currentPath}/${item.name}`, name: item.name });
    }
  }

  function navigateUp() {
    const vaultDepth = vaultPath.split("/").length;
    const parts = currentPath.split("/");
    if (parts.length <= vaultDepth) return;
    parts.pop();
    loadDir(parts.join("/"));
  }

  const isAtRoot = currentPath === vaultPath;
  const relPath = isAtRoot ? "" : currentPath.replace(vaultPath + "/", "");
  const pathParts = relPath ? relPath.split("/") : [];
  const vaultName = vaultPath.split("/").pop();

  // Setup / Settings
  if (phase === "setup" || showSettings) {
    const isSettings = showSettings && phase !== "setup";
    return (
      <div className="screen vault-screen">
        <header className="vault-nav">
          {isSettings ? (
            <button className="vault-back" onClick={() => setShowSettings(false)} aria-label="Back">
              <BackIcon /><span>Vault</span>
            </button>
          ) : (
            <span className="vault-nav-title">Vault</span>
          )}
          {isSettings && <span className="vault-nav-title">Settings</span>}
        </header>
        <div className="scroll-body vault-setup">
          <div className="vault-setup-icon"><VaultBookIcon /></div>
          <h2 className="vault-setup-title">
            {isSettings ? "Change Vault" : "Connect Your Vault"}
          </h2>
          <p className="vault-setup-desc">
            Enter the path to your Obsidian vault, relative to your phone's internal storage root.
          </p>
          <div className="vault-path-input-wrap">
            <label className="vault-path-label" htmlFor="vault-path-input">Vault Path</label>
            <input
              id="vault-path-input"
              className="vault-path-input"
              type="text"
              value={inputPath}
              onChange={e => setInputPath(e.target.value)}
              placeholder="e.g. Obsidian/My Vault"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck="false"
              onKeyDown={e => e.key === "Enter" && saveVaultPath()}
            />
            <p className="vault-path-hint">
              Common: <code>Obsidian/VaultName</code> · <code>Documents/Notes</code>
            </p>
          </div>
          <button
            className="vault-connect-btn"
            onClick={saveVaultPath}
            disabled={!inputPath.trim()}
          >
            {isSettings ? "Save & Reload" : "Connect Vault"}
          </button>
        </div>
      </div>
    );
  }

  // Permission
  if (phase === "permission") {
    return (
      <div className="screen vault-screen">
        <header className="vault-nav">
          <span className="vault-nav-title">Vault</span>
        </header>
        <div className="scroll-body vault-state-wrap">
          <div className="vault-state-emoji">🔐</div>
          <h2 className="vault-state-title">Storage Permission Needed</h2>
          <p className="vault-state-desc">
            To read your Obsidian vault, the app needs access to your device's storage.
          </p>
          <button className="vault-connect-btn" onClick={requestPermission}>
            Grant Permission
          </button>
          <p className="vault-perm-hint">
            If no prompt appears, enable "Files and media" for this app in Android Settings.
          </p>
        </div>
      </div>
    );
  }

  // Error
  if (phase === "error") {
    return (
      <div className="screen vault-screen">
        <header className="vault-nav">
          <span className="vault-nav-title">Vault</span>
          <button className="vault-settings-btn" onClick={() => setShowSettings(true)} aria-label="Vault settings">
            <SettingsIcon />
          </button>
        </header>
        <div className="scroll-body vault-state-wrap">
          <div className="vault-state-emoji">⚠️</div>
          <h2 className="vault-state-title">Could not open vault</h2>
          <p className="vault-state-desc vault-error-msg">{errorMsg}</p>
          <button className="vault-connect-btn" onClick={() => loadDir(vaultPath)}>Retry</button>
          <button className="vault-change-btn" onClick={() => setShowSettings(true)}>Change Path</button>
        </div>
      </div>
    );
  }

  // Loading
  if (phase === "loading" || phase === "init") {
    return (
      <div className="screen vault-screen">
        <header className="vault-nav">
          <span className="vault-nav-title">Vault</span>
        </header>
        <div className="scroll-body vault-state-wrap">
          <div className="vault-spinner" aria-label="Loading" role="status" />
        </div>
      </div>
    );
  }

  // Browse
  return (
    <div className="screen vault-screen">
      <header className="vault-nav">
        {!isAtRoot ? (
          <button className="vault-back" onClick={navigateUp} aria-label="Go up">
            <BackIcon />
            <span>{pathParts.length > 1 ? pathParts[pathParts.length - 2] : vaultName}</span>
          </button>
        ) : (
          <span className="vault-nav-title">{vaultName}</span>
        )}
        <button className="vault-settings-btn" onClick={() => setShowSettings(true)} aria-label="Vault settings">
          <SettingsIcon />
        </button>
      </header>

      {!isAtRoot && (
        <div className="vault-breadcrumb" aria-label="Path">
          <button className="vault-crumb" onClick={() => loadDir(vaultPath)}>{vaultName}</button>
          {pathParts.map((part, i) => (
            <span key={i} className="vault-crumb-segment">
              <span className="vault-crumb-sep" aria-hidden="true">/</span>
              {i < pathParts.length - 1 ? (
                <button
                  className="vault-crumb"
                  onClick={() => loadDir(`${vaultPath}/${pathParts.slice(0, i + 1).join("/")}`)}
                >
                  {part}
                </button>
              ) : (
                <span className="vault-crumb vault-crumb-active">{part}</span>
              )}
            </span>
          ))}
        </div>
      )}

      <div className="scroll-body vault-body">
        {items.length === 0 ? (
          <p className="vault-empty">No markdown files or folders here.</p>
        ) : (
          <ul className="vault-list" aria-label="Vault contents">
            {items.map(item => (
              <li key={item.name}>
                <button className="vault-row" onClick={() => navigateTo(item)}>
                  <span className={`vault-row-icon vault-row-icon--${item.type === "directory" ? "folder" : "file"}`}>
                    {item.type === "directory" ? <FolderIcon /> : <NoteIcon />}
                  </span>
                  <span className="vault-row-name">
                    {item.type === "directory" ? item.name : item.name.replace(/\.md$/, "")}
                  </span>
                  <span className="vault-row-arrow" aria-hidden="true">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="m9 18 6-6-6-6" />
                    </svg>
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
        <div className="list-pad" />
      </div>
    </div>
  );
}
