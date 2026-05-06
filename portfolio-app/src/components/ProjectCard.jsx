import "./ProjectCard.css";

export default function ProjectCard({ project, onClick }) {
  return (
    <div
      className="card"
      onClick={onClick}
      style={{ "--card-accent": project.color }}
    >
      <div className="card-top">
        <div className="card-icon">{project.icon}</div>
        <span className={`card-status status-${project.status.toLowerCase().replace(" ", "-")}`}>
          {project.status}
        </span>
      </div>
      <h3 className="card-title">{project.title}</h3>
      <p className="card-desc">{project.description}</p>
      <div className="card-footer">
        <div className="card-tags">
          {project.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="tag">
              {tag}
            </span>
          ))}
        </div>
        <span className="card-version">v{project.version}</span>
      </div>
    </div>
  );
}
