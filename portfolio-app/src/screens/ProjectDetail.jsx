import "./ProjectDetail.css";

function statusClass(status) {
  return "badge badge-" + status.toLowerCase().replace(/\s+/g, "-");
}

const BackIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
    aria-hidden="true">
    <path d="m15 18-6-6 6-6" />
  </svg>
);

export default function ProjectDetail({ project, onBack }) {
  return (
    <div className="screen detail-screen" style={{ "--c": project.color }}>

      {/* Nav bar */}
      <header className="detail-nav">
        <button className="back-btn" onClick={onBack} aria-label="Go back">
          <BackIcon />
          <span>Projects</span>
        </button>
        <span className={statusClass(project.status)}>{project.status}</span>
      </header>

      {/* Scrollable content */}
      <div className="scroll-body detail-body">

        {/* Hero */}
        <div className="detail-hero" aria-label={`${project.title} icon`}>
          <div className="detail-glow" aria-hidden="true" />
          <div className="detail-icon" aria-hidden="true">{project.icon}</div>
          <h1 className="detail-title">{project.title}</h1>
          <div className="detail-meta-row">
            <span className="detail-cat">{project.category}</span>
            {project.year && <span className="detail-year">{project.year}</span>}
            <span className="detail-version">v{project.version}</span>
          </div>
        </div>

        {/* Sections */}
        <div className="detail-sections">

          <section className="detail-section">
            <h2 className="section-label">About</h2>
            <p className="detail-text">{project.details || project.description}</p>
          </section>

          <section className="detail-section">
            <h2 className="section-label">Tags</h2>
            <div className="detail-tags" aria-label="Project tags">
              {project.tags.map((tag) => (
                <span key={tag} className="detail-tag">{tag}</span>
              ))}
            </div>
          </section>

          {project.links && project.links.length > 0 && (
            <section className="detail-section">
              <h2 className="section-label">Links</h2>
              <ul className="detail-links">
                {project.links.map((link) => (
                  <li key={link.url}>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="detail-link"
                    >
                      <span>{link.label}</span>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
                        strokeLinejoin="round" aria-hidden="true">
                        <path d="M7 17 17 7M7 7h10v10" />
                      </svg>
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        <div className="list-pad" />
      </div>
    </div>
  );
}
