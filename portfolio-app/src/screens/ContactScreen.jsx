import { profile } from "../data/profile";
import "./ContactScreen.css";

/* ── Icons ─────────────────────────────────────────────── */
const icons = {
  github: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z" />
    </svg>
  ),
  email: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="2" y="4" width="20" height="16" rx="2.5" />
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
    </svg>
  ),
  discord: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057c.002.022.015.043.03.056a19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z" />
    </svg>
  ),
  twitter: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.747l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  ),
  youtube: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
    </svg>
  ),
  linkedin: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  ),
  reddit: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z" />
    </svg>
  ),
  instagram: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z" />
    </svg>
  ),
  telegram: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
    </svg>
  ),
  modrinth: (
    <svg viewBox="0 0 512 514" fill="currentColor" aria-hidden="true">
      <path d="M255.9 0C114.3 0 .1 114.2 0 255.8c0 90.9 47.8 170.6 119.5 215.1l19.7-48.3c-7.5-4.9-14.7-10.2-21.6-16L94.9 421c-45.5-37.8-74.9-94.3-75.5-157.7h45.9c.6 44.8 19.2 85.2 49.1 114.4l-16.2 39.8c-2.9-2.7-5.8-5.5-8.5-8.4-34-36.2-54.9-84.7-54.9-138.1C34.8 133.4 133.4 34.8 255.9 34.8c5.6 0 11.1.2 16.6.6l-6 44.7c-3.5-.2-7.1-.4-10.6-.4-120.6 0-218.8 98.2-218.8 218.9 0 25.9 4.5 50.7 12.8 73.7l-19.2 47c-17.5-35.4-27.4-75.1-27.4-117 0-120.6 80.6-222 190.2-254.2l9-43.8C195.7 3.3 225.4 0 255.9 0z"/>
      <path d="M492.8 226.2C481 109.9 384.9 19 267.3 12.8l-9.1 44c102.7 8.4 185.7 90.5 195.2 193l39.4-23.6zM276.9 456.8c-6.8.7-13.7 1.1-20.7 1.1-29.5 0-57.5-6.2-82.8-17.4l-19.7 48.3C181.8 501.4 218.1 512 256.2 512c11.2 0 22.2-.9 33-2.5l-12.3-52.7zM416 95.4c36.5 37.5 59.1 88.6 59.1 145.1 0 37.3-9.8 72.3-27 102.7l38.1 30.5C506.4 340.8 520 299.3 520 254.8 520 184.1 492.3 119.9 447 72.9L416 95.4z"/>
    </svg>
  ),
  curseforge: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M6.608 3.646L4.65 5.878l1.958 2.23H3.795l-1.958 2.23 1.958 2.232H.983l-1.4 1.597c.69 4.784 4.814 8.465 9.795 8.465 5.488 0 9.934-4.446 9.934-9.934 0-5.128-3.875-9.358-8.837-9.91L9.44 1.33a9.899 9.899 0 0 0-2.832 2.316zm8.16 10.042l-2.386-1.384 1.382 2.386-1.382 2.386-2.386-1.382 1.384 2.386H9.03l-1.384-2.386L6.26 17.06l-1.382-2.386 1.382-2.386-2.386 1.384V11.33l2.386 1.382-1.382-2.386 1.382-2.384 2.386 1.382L9.03 6.94h1.352l1.384 2.384 2.384-1.382 1.384 2.384-1.384 2.386 2.386-1.382v1.358z"/>
    </svg>
  ),
  website: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  ),
  twitch: (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714z" />
    </svg>
  ),
};

/* ── Link definitions ──────────────────────────────────── */
const SOCIAL_LINKS = [
  { id: "github",    label: "GitHub",      hint: "See my code",           href: (s) => s.github },
  { id: "website",   label: "Website",     hint: "My personal site",      href: (s) => s.website },
  { id: "youtube",   label: "YouTube",     hint: "Watch my videos",       href: (s) => s.youtube },
  { id: "twitch",    label: "Twitch",      hint: "Watch me live",         href: (s) => s.twitch },
  { id: "instagram", label: "Instagram",   hint: "Photos & updates",      href: (s) => s.instagram },
  { id: "twitter",   label: "Twitter / X", hint: "Thoughts & updates",    href: (s) => s.twitter },
  { id: "reddit",    label: "Reddit",      hint: "Discussions",           href: (s) => s.reddit },
  { id: "linkedin",  label: "LinkedIn",    hint: "Professional profile",  href: (s) => s.linkedin },
];

const CONTACT_LINKS = [
  { id: "email",    label: "Email",    hint: "Send me a message", href: (s) => s.email    ? `mailto:${s.email}`    : "" },
  { id: "discord",  label: "Discord",  hint: "Chat with me",      href: (s) => s.discord },
  { id: "telegram", label: "Telegram", hint: "Message me",        href: (s) => s.telegram },
];

const GAMING_LINKS = [
  { id: "modrinth",   label: "Modrinth",   hint: "My mods & modpacks",  href: (s) => s.modrinth },
  { id: "curseforge", label: "CurseForge", hint: "My mods & modpacks",  href: (s) => s.curseforge },
];

/* ── Shared row component ──────────────────────────────── */
function LinkRow({ link, social }) {
  const href = link.href(social);
  if (!href) return null;
  return (
    <li>
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="contact-row"
        aria-label={link.label}
      >
        <span className="contact-icon">{icons[link.id]}</span>
        <span className="contact-text">
          <span className="contact-label">{link.label}</span>
          <span className="contact-hint">{link.hint}</span>
        </span>
        <svg className="contact-arrow" width="16" height="16"
          viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
          aria-hidden="true">
          <path d="m9 18 6-6-6-6" />
        </svg>
      </a>
    </li>
  );
}

function LinkGroup({ title, links, social }) {
  const visible = links.filter((l) => !!l.href(social));
  if (visible.length === 0) return null;
  return (
    <div className="contact-group">
      <h2 className="contact-group-label">{title}</h2>
      <ul className="contact-list" aria-label={title}>
        {links.map((l) => <LinkRow key={l.id} link={l} social={social} />)}
      </ul>
    </div>
  );
}

/* ── Screen ────────────────────────────────────────────── */
export default function ContactScreen() {
  const { social, status } = profile;

  const anyVisible = [...SOCIAL_LINKS, ...CONTACT_LINKS, ...GAMING_LINKS]
    .some((l) => !!l.href(social));

  return (
    <div className="screen contact-screen">
      <header className="screen-header">
        <h1 className="screen-title">Contact</h1>
        <p className="screen-sub">Get in touch</p>
      </header>

      <main className="scroll-body contact-body">

        {/* Status card */}
        {status && (
          <div className="status-card" aria-label="Current status">
            <span className="status-dot" aria-hidden="true" />
            <div className="status-text">
              <span className="status-heading">Currently</span>
              <span className="status-value">{status}</span>
            </div>
          </div>
        )}

        {anyVisible ? (
          <>
            <LinkGroup title="Social"   links={SOCIAL_LINKS}  social={social} />
            <LinkGroup title="Messaging" links={CONTACT_LINKS} social={social} />
            <LinkGroup title="Gaming"   links={GAMING_LINKS}  social={social} />
          </>
        ) : (
          <div className="empty">
            <span className="empty-icon" aria-hidden="true">📬</span>
            <p className="empty-title">No links yet</p>
            <p className="empty-sub">Add your details in <code>src/data/profile.js</code></p>
          </div>
        )}

        <p className="edit-hint">
          Edit <code>src/data/profile.js</code> to add or hide links
        </p>

        <div className="list-pad" />
      </main>
    </div>
  );
}
