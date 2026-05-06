import "./ProjectCard.css";

function statusClass(status) {
  return "badge badge-" + status.toLowerCase().replace(/\s+/g, "-");
}

export default function ProjectCard({ project, onClick }) {
  return (
    <article
      className="card"
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`View ${project.title}`}
      onKeyDown={(e) => e.key === "Enter" && onClick()}
      style={{ "--c": project.color }}
    >
      <div className="card-accent-bar" />

      <div className="card-head">
        <span className="card-icon" aria-hidden="true">{project.icon}</span>
        <span className={statusClass(project.status)}>{project.status}</span>
      </div>

      <div className="card-body">
        <h3 className="card-title">{project.title}</h3>
        <p className="card-desc">{project.description}</p>
      </div>

      <footer className="card-foot">
        <div className="card-tags" aria-label="Tags">
          {project.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
        <div className="card-meta">
          <span className="card-year">{project.year}</span>
          <span className="card-arrow" aria-hidden="true">→</span>
        </div>
      </footer>
    </article>
  );
}
