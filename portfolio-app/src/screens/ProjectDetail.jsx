import "./ProjectDetail.css";

export default function ProjectDetail({ project, onBack }) {
  return (
    <div className="detail" style={{ "--card-accent": project.color }}>
      <div className="detail-header">
        <button className="back-btn" onClick={onBack}>
          <span className="back-arrow">←</span>
          <span>Back</span>
        </button>
        <span className={`card-status status-${project.status.toLowerCase().replace(" ", "-")}`}>
          {project.status}
        </span>
      </div>

      <div className="detail-scroll">
        <div className="detail-hero">
          <div className="detail-icon">{project.icon}</div>
          <h1 className="detail-title">{project.title}</h1>
          <p className="detail-version">Version {project.version}</p>
        </div>

        <div className="detail-body">
          <section className="detail-section">
            <h2>About</h2>
            <p>{project.details || project.description}</p>
          </section>

          <section className="detail-section">
            <h2>Category</h2>
            <div className="detail-category">
              <span className="cat-badge">{project.category}</span>
            </div>
          </section>

          <section className="detail-section">
            <h2>Tags</h2>
            <div className="detail-tags">
              {project.tags.map((tag) => (
                <span key={tag} className="detail-tag">
                  {tag}
                </span>
              ))}
            </div>
          </section>

          {project.links && project.links.length > 0 && (
            <section className="detail-section">
              <h2>Links</h2>
              <div className="detail-links">
                {project.links.map((link) => (
                  <a
                    key={link.url}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="detail-link"
                  >
                    {link.label}
                    <span className="link-arrow">↗</span>
                  </a>
                ))}
              </div>
            </section>
          )}
        </div>
        <div className="scroll-pad" />
      </div>
    </div>
  );
}
