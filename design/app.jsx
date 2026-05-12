// Younds — main desktop window app
// Cozy cabin music downloader. Sleepy bear edition.

const { useState, useEffect, useRef, useMemo } = React;

// ─── Iconography (simple line icons, no complex SVG) ───────────────────────
const Icon = {
  Search: ({ s = 18 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <circle cx="11" cy="11" r="7" />
      <line x1="16.5" y1="16.5" x2="21" y2="21" />
    </svg>
  ),
  Link: ({ s = 18 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <rect x="3" y="9" width="9" height="6" rx="3" />
      <rect x="12" y="9" width="9" height="6" rx="3" />
    </svg>
  ),
  Library: ({ s = 18 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <line x1="5" y1="4" x2="5" y2="20" /><line x1="9" y1="4" x2="9" y2="20" />
      <line x1="13" y1="4" x2="13" y2="20" /><rect x="16" y="5" width="4" height="15" rx="1" transform="rotate(-12 18 12)" />
    </svg>
  ),
  Download: ({ s = 18 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="3" x2="12" y2="15" /><polyline points="6 11 12 17 18 11" /><line x1="4" y1="20" x2="20" y2="20" />
    </svg>
  ),
  Settings: ({ s = 18 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <circle cx="12" cy="12" r="3" />
      <circle cx="12" cy="12" r="9" />
    </svg>
  ),
  Compass: ({ s = 18 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9" /><polygon points="14.5 9.5 9.5 11.5 9.5 14.5 14.5 12.5" />
    </svg>
  ),
  Pause: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14" rx="1" /><rect x="14" y="5" width="4" height="14" rx="1" /></svg>
  ),
  Play: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20" /></svg>
  ),
  X: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><line x1="6" y1="6" x2="18" y2="18" /><line x1="18" y1="6" x2="6" y2="18" /></svg>
  ),
  Folder: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z" /></svg>
  ),
  Check: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 12 10 18 20 6" /></svg>
  ),
  Sparkles: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l1.6 5.2L19 9l-5.4 1.8L12 16l-1.6-5.2L5 9l5.4-1.8L12 2Z" /></svg>
  ),
  Pine: ({ s = 14 }) => (
    <svg width={s} height={s} viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 18 10 14 10 19 17 13 17 13 22 11 22 11 17 5 17 10 10 6 10" /></svg>
  ),
};

// ─── Window chrome (Windows 11 style) ─────────────────────────────────────
function WinChrome({ children, theme }) {
  return (
    <div className="win-titlebar">
      <div className="win-tb-left">
        <YoundsLogo size={18} />
        <span className="win-tb-title">Younds</span>
        <span className="win-tb-sep">·</span>
        <span className="win-tb-sub">Music Downloader</span>
      </div>
      <div className="win-tb-mid">{children}</div>
      <div className="win-tb-controls">
        <button className="win-tb-btn" aria-label="Minimize"><svg width="10" height="10" viewBox="0 0 10 10"><line x1="0" y1="5" x2="10" y2="5" stroke="currentColor" strokeWidth="1" /></svg></button>
        <button className="win-tb-btn" aria-label="Maximize"><svg width="10" height="10" viewBox="0 0 10 10"><rect x="0.5" y="0.5" width="9" height="9" fill="none" stroke="currentColor" strokeWidth="1" /></svg></button>
        <button className="win-tb-btn win-tb-close" aria-label="Close"><svg width="10" height="10" viewBox="0 0 10 10"><line x1="0" y1="0" x2="10" y2="10" stroke="currentColor" strokeWidth="1" /><line x1="10" y1="0" x2="0" y2="10" stroke="currentColor" strokeWidth="1" /></svg></button>
      </div>
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────────────
function Sidebar({ active, onChange, density, mascot }) {
  const items = [
    { id: "discover", label: "Discover", icon: Icon.Compass },
    { id: "search", label: "Search", icon: Icon.Search },
    { id: "downloads", label: "Downloads", icon: Icon.Download, badge: 2 },
    { id: "library", label: "Library", icon: Icon.Library },
    { id: "settings", label: "Settings", icon: Icon.Settings },
  ];
  return (
    <aside className="sidebar" data-density={density}>
      <div className="sb-brand">
        <YoundsLogo size={32} />
        <div>
          <div className="sb-brand-name">Younds</div>
          <div className="sb-brand-tag">v1.4 · cabin build</div>
        </div>
      </div>

      <nav className="sb-nav">
        {items.map((it) => {
          const Ico = it.icon;
          return (
            <button
              key={it.id}
              className={`sb-item ${active === it.id ? "is-active" : ""}`}
              onClick={() => onChange(it.id)}
            >
              <Ico s={18} />
              <span>{it.label}</span>
              {it.badge && <span className="sb-badge">{it.badge}</span>}
            </button>
          );
        })}
      </nav>

      <div className="sb-section">Recent</div>
      <div className="sb-recent">
        <div className="sb-recent-item"><span className="sb-dot" style={{ background: "#c98a4a" }} /> Bon Iver — Holocene</div>
        <div className="sb-recent-item"><span className="sb-dot" style={{ background: "#7a8a4a" }} /> Fleet Foxes — Helplessness</div>
        <div className="sb-recent-item"><span className="sb-dot" style={{ background: "#a05c4a" }} /> Sufjan Stevens — Mystery</div>
      </div>

      {mascot !== "off" && (
        <div className="sb-mascot">
          <YoundsBear size={mascot === "big" ? 130 : 90} mood="sleepy" />
          <div className="sb-mascot-cap">
            <em>"shhh… tracking the song quietly."</em>
          </div>
        </div>
      )}
    </aside>
  );
}

// ─── Search hero ──────────────────────────────────────────────────────────
function SearchHero({ query, setQuery, onSubmit, mode, setMode, format, setFormat, quality, setQuality, density }) {
  const inputRef = useRef(null);
  const isUrl = mode === "url";

  return (
    <section className="hero" data-density={density}>
      <div className="hero-eyebrow">
        <Icon.Pine s={12} /> <span>Cabin · windows open · snow outside</span>
      </div>
      <h1 className="hero-h1">
        What track shall we bring down from the w<span className="hero-h1-accent">oo</span>ds today?
      </h1>
      <p className="hero-sub">
        Paste a link or search by title and artist. The bear finds it; I tidy up the metadata.
      </p>

      <div className="searchbar">
        <div className="searchbar-modes">
          <button className={`mode-btn ${!isUrl ? "is-on" : ""}`} onClick={() => setMode("search")}>
            <Icon.Search s={14} /> Search
          </button>
          <button className={`mode-btn ${isUrl ? "is-on" : ""}`} onClick={() => setMode("url")}>
            <Icon.Link s={14} /> Paste URL
          </button>
        </div>

        <div className="searchbar-row">
          <div className="searchbar-input">
            <span className="searchbar-icon">{isUrl ? <Icon.Link s={18} /> : <Icon.Search s={18} />}</span>
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onSubmit()}
              placeholder={isUrl
                ? "https://www.youtube.com/watch?v=…   or   soundcloud.com/…"
                : "Search by title, artist, album…  e.g. bon iver re: stacks"}
            />
            {query && (
              <button className="searchbar-clear" onClick={() => setQuery("")} aria-label="Clear"><Icon.X s={12} /></button>
            )}
          </div>
          <button className="btn-primary" onClick={onSubmit}>
            <Icon.Download s={14} /> Download
          </button>
        </div>

        <div className="searchbar-options">
          <div className="opt-group">
            <span className="opt-label">Format</span>
            <div className="seg">
              {["MP3", "FLAC", "M4A", "WAV"].map((f) => (
                <button key={f} className={`seg-btn ${format === f ? "is-on" : ""}`} onClick={() => setFormat(f)}>{f}</button>
              ))}
            </div>
          </div>

          <div className="opt-group">
            <span className="opt-label">Quality</span>
            <div className="seg">
              {format === "FLAC"
                ? ["lossless"].map((q) => (
                    <button key={q} className="seg-btn is-on">{q}</button>
                  ))
                : ["128", "192", "256", "320"].map((q) => (
                    <button key={q} className={`seg-btn ${quality === q ? "is-on" : ""}`} onClick={() => setQuality(q)}>{q} kbps</button>
                  ))}
            </div>
          </div>

          <div className="opt-spacer" />

          <button className="opt-link"><Icon.Folder s={12} /> C:\Users\You\Music\Younds</button>
        </div>
      </div>

      <div className="hero-chips">
        <span className="chip-label">Tonight's picks:</span>
        {[
          "iver re:stacks",
          "fleet foxes mykonos",
          "phoebe bridgers garden song",
          "novo amor anchor",
        ].map((s) => (
          <button key={s} className="chip" onClick={() => { setMode("search"); setQuery(s); }}>{s}</button>
        ))}
      </div>
    </section>
  );
}

// ─── Downloads queue ──────────────────────────────────────────────────────
function DownloadsList({ items, onPause, onCancel }) {
  return (
    <section className="downloads">
      <header className="dl-head">
        <h2>In progress & recent</h2>
        <div className="dl-head-meta">
          <span><Icon.Sparkles s={12} /> 320 kbps · MP3 default</span>
          <span className="dl-sep">·</span>
          <span>{items.filter(i => i.status === "downloading").length} active</span>
        </div>
      </header>
      <div className="dl-list">
        {items.map((it) => (
          <DownloadRow key={it.id} item={it} onPause={onPause} onCancel={onCancel} />
        ))}
      </div>
    </section>
  );
}

function DownloadRow({ item, onPause, onCancel }) {
  const isDown = item.status === "downloading";
  const isDone = item.status === "done";
  const isQueued = item.status === "queued";

  return (
    <div className={`dl-row dl-${item.status}`}>
      <div className="dl-cover" style={{ background: item.cover }}>
        <span>{item.coverEmoji || "♪"}</span>
      </div>

      <div className="dl-meta">
        <div className="dl-title">
          <strong>{item.title}</strong>
          <span className="dl-artist">— {item.artist}</span>
        </div>
        <div className="dl-sub">
          <span className="dl-source">{item.source}</span>
          <span className="dl-sep">·</span>
          <span>{item.format} · {item.quality}</span>
          <span className="dl-sep">·</span>
          <span>{item.size}</span>
          {isDown && <><span className="dl-sep">·</span><span className="dl-eta">{item.eta}</span></>}
          {isQueued && <><span className="dl-sep">·</span><span>waiting in line</span></>}
        </div>

        {!isDone && (
          <div className="dl-bar">
            <div className="dl-bar-fill" style={{
              width: `${item.progress}%`,
              opacity: isQueued ? 0.4 : 1,
            }} />
          </div>
        )}
        {isDone && (
          <div className="dl-done-row">
            <Icon.Check s={12} /> Saved to <button className="dl-folder">Younds / Winter 2026</button>
            <span className="dl-sep">·</span>
            <span className="dl-time">{item.doneAt} ago</span>
          </div>
        )}
      </div>

      <div className="dl-actions">
        {isDown && (
          <>
            <span className="dl-percent">{item.progress}%</span>
            <button className="dl-icon-btn" onClick={() => onPause(item.id)}><Icon.Pause s={12} /></button>
            <button className="dl-icon-btn" onClick={() => onCancel(item.id)}><Icon.X s={12} /></button>
          </>
        )}
        {isQueued && (
          <button className="dl-icon-btn" onClick={() => onCancel(item.id)}><Icon.X s={12} /></button>
        )}
        {isDone && (
          <>
            <button className="dl-icon-btn"><Icon.Play s={12} /></button>
            <button className="dl-icon-btn"><Icon.Folder s={12} /></button>
          </>
        )}
      </div>
    </div>
  );
}

// ─── Status bar ───────────────────────────────────────────────────────────
function StatusBar({ items }) {
  const active = items.filter(i => i.status === "downloading").length;
  return (
    <div className="statusbar">
      <div className="status-left">
        <span className="status-dot" /> Connected · forest online
      </div>
      <div className="status-mid">
        {active > 0
          ? <>{active} download{active === 1 ? "" : "s"} in progress · 1.2 MB/s · ETA ~ 0:42</>
          : <>All quiet. The bear is dozing.</>}
      </div>
      <div className="status-right">
        <span>Library: 1,284 tracks · 8.4 GB</span>
      </div>
    </div>
  );
}

// ─── Sample data ──────────────────────────────────────────────────────────
const SAMPLE = [
  {
    id: 1, status: "downloading", progress: 64,
    title: "Holocene", artist: "Bon Iver",
    source: "youtube.com/watch?v=TWcyIp…", format: "FLAC", quality: "lossless",
    size: "28.4 MB", eta: "ETA 0:38",
    cover: "linear-gradient(135deg,#3d5c3a,#7a8a4a)", coverEmoji: "❄",
  },
  {
    id: 2, status: "downloading", progress: 23,
    title: "Re: Stacks", artist: "Bon Iver",
    source: "soundcloud.com/boniver/restacks", format: "MP3", quality: "320 kbps",
    size: "12.1 MB", eta: "ETA 1:12",
    cover: "linear-gradient(135deg,#a05c4a,#c98a4a)", coverEmoji: "♫",
  },
  {
    id: 3, status: "queued", progress: 0,
    title: "White Winter Hymnal", artist: "Fleet Foxes",
    source: "youtube.com/watch?v=Lwlt9…", format: "MP3", quality: "320 kbps",
    size: "~9.6 MB", eta: "",
    cover: "linear-gradient(135deg,#7a8a4a,#c8b56a)", coverEmoji: "🌲",
  },
  {
    id: 4, status: "done",
    title: "Mykonos", artist: "Fleet Foxes",
    source: "youtube.com", format: "MP3", quality: "320 kbps",
    size: "11.3 MB", doneAt: "2 min",
    progress: 100,
    cover: "linear-gradient(135deg,#c98a4a,#e8c89a)", coverEmoji: "☼",
  },
  {
    id: 5, status: "done",
    title: "Garden Song", artist: "Phoebe Bridgers",
    source: "soundcloud.com", format: "FLAC", quality: "lossless",
    size: "24.8 MB", doneAt: "14 min",
    progress: 100,
    cover: "linear-gradient(135deg,#5a4a8a,#a09acb)", coverEmoji: "✿",
  },
];

// ─── Tweak defaults ───────────────────────────────────────────────────────
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "daylight",
  "density": "regular",
  "mascot": "regular",
  "accent": "#c98a4a"
}/*EDITMODE-END*/;

// ─── Main App ─────────────────────────────────────────────────────────────
function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);

  const [active, setActive] = useState("search");
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("search");
  const [format, setFormat] = useState("MP3");
  const [quality, setQuality] = useState("320");
  const [items, setItems] = useState(SAMPLE);

  // Subtle progress animation for "downloading" rows
  useEffect(() => {
    const id = setInterval(() => {
      setItems((cur) => cur.map((it) => {
        if (it.status !== "downloading") return it;
        const next = Math.min(99, it.progress + Math.random() * 2.2);
        return { ...it, progress: Math.round(next) };
      }));
    }, 700);
    return () => clearInterval(id);
  }, []);

  const submit = () => {
    if (!query.trim()) return;
    const newItem = {
      id: Date.now(),
      status: "queued",
      progress: 0,
      title: mode === "url" ? "New track" : query.split(" ").slice(0, 3).join(" "),
      artist: mode === "url" ? "from link" : "—",
      source: mode === "url" ? query.slice(0, 36) + "…" : "youtube.com (top result)",
      format, quality: format === "FLAC" ? "lossless" : `${quality} kbps`,
      size: "~10 MB", eta: "",
      cover: "linear-gradient(135deg,#3d5c3a,#a07050)", coverEmoji: "♪",
    };
    setItems((cur) => [newItem, ...cur]);
    setQuery("");
  };

  const onPause = (id) => setItems((cur) => cur.map((it) => it.id === id ? { ...it, status: "queued" } : it));
  const onCancel = (id) => setItems((cur) => cur.filter((it) => it.id !== id));

  return (
    <div className={`app theme-${t.theme}`} style={{ "--accent": t.accent }}>
      <WinChrome theme={t.theme}>
        <div className="tb-tabs">
          <button className="tb-tab is-on">Studio</button>
          <button className="tb-tab">Library</button>
          <button className="tb-tab">Journal</button>
        </div>
      </WinChrome>

      <div className="app-body">
        <Sidebar active={active} onChange={setActive} density={t.density} mascot={t.mascot} />

        <main className="main">
          <div className="main-scroll">
            <SearchHero
              query={query} setQuery={setQuery} onSubmit={submit}
              mode={mode} setMode={setMode}
              format={format} setFormat={setFormat}
              quality={quality} setQuality={setQuality}
              density={t.density}
            />

            <DownloadsList items={items} onPause={onPause} onCancel={onCancel} />
          </div>
        </main>
      </div>

      <StatusBar items={items} />

      <TweaksPanel title="Tweaks">
        <TweakSection label="Atmosphere" />
        <TweakRadio
          label="Theme"
          value={t.theme}
          options={["daylight", "firelight", "night"]}
          onChange={(v) => setTweak("theme", v)}
        />
        <TweakColor
          label="Accent"
          value={t.accent}
          options={["#c98a4a", "#3d5c3a", "#a05c4a", "#5a6c8a"]}
          onChange={(v) => setTweak("accent", v)}
        />
        <TweakSection label="Layout" />
        <TweakRadio
          label="Density"
          value={t.density}
          options={["compact", "regular", "comfy"]}
          onChange={(v) => setTweak("density", v)}
        />
        <TweakSection label="Mascot" />
        <TweakRadio
          label="Bear"
          value={t.mascot}
          options={["off", "regular", "big"]}
          onChange={(v) => setTweak("mascot", v)}
        />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
