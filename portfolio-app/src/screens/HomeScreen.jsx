import { useState } from "react";
import { projects, categories } from "../data/projects";
import ProjectCard from "../components/ProjectCard";
import "./HomeScreen.css";

export default function HomeScreen({ onSelectProject }) {
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");

  const filtered = projects.filter((p) => {
    const matchCat = activeCategory === "All" || p.category === activeCategory;
    const matchSearch =
      p.title.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase()) ||
      p.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()));
    return matchCat && matchSearch;
  });

  return (
    <div className="home">
      <div className="home-header">
        <div className="header-top">
          <div className="brand">
            <span className="brand-icon">⚡</span>
            <div>
              <h1 className="brand-name">My Portfolio</h1>
              <p className="brand-sub">Everything I've built</p>
            </div>
          </div>
          <div className="stats">
            <div className="stat">
              <span className="stat-num">{projects.length}</span>
              <span className="stat-label">Projects</span>
            </div>
          </div>
        </div>

        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="search-clear" onClick={() => setSearch("")}>
              ✕
            </button>
          )}
        </div>

        <div className="categories">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`cat-pill ${activeCategory === cat ? "active" : ""}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="projects-scroll">
        {filtered.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">🔭</span>
            <p>Nothing found</p>
            <span>Try a different search or category</span>
          </div>
        ) : (
          <div className="projects-grid">
            {filtered.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={() => onSelectProject(project)}
              />
            ))}
          </div>
        )}
        <div className="scroll-pad" />
      </div>
    </div>
  );
}
