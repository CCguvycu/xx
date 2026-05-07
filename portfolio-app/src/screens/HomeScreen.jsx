import { useState } from "react";
import { projects, categories } from "../data/projects";
import ProjectCard from "../components/ProjectCard";
import "./HomeScreen.css";

const SearchIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"
    aria-hidden="true">
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </svg>
);

const ClearIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" aria-hidden="true">
    <path d="M18 6 6 18M6 6l12 12" />
  </svg>
);

export default function HomeScreen({ onSelectProject }) {
  const [activeCategory, setActiveCategory] = useState("All");
  const [search, setSearch] = useState("");

  const filtered = projects.filter((p) => {
    const matchCat = activeCategory === "All" || p.category === activeCategory;
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      p.title.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.tags.some((t) => t.toLowerCase().includes(q));
    return matchCat && matchSearch;
  });

  return (
    <div className="screen home-screen">
      <header className="screen-header home-header">
        <div className="home-title-row">
          <h1 className="screen-title">Projects</h1>
          <span className="home-count" aria-label={`${projects.length} projects`}>
            {projects.length}
          </span>
        </div>

        <div className="search-bar" role="search">
          <span className="search-icon"><SearchIcon /></span>
          <input
            type="search"
            placeholder="Search projects…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search projects"
          />
          {search && (
            <button
              className="search-clear"
              onClick={() => setSearch("")}
              aria-label="Clear search"
            >
              <ClearIcon />
            </button>
          )}
        </div>

        <div className="cat-row" role="group" aria-label="Filter by category">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`cat-pill ${activeCategory === cat ? "active" : ""}`}
              onClick={() => setActiveCategory(cat)}
              aria-pressed={activeCategory === cat}
            >
              {cat}
            </button>
          ))}
        </div>
      </header>

      <main className="scroll-body projects-body">
        {filtered.length === 0 ? (
          <div className="empty" role="status">
            <span className="empty-icon" aria-hidden="true">🔭</span>
            <p className="empty-title">Nothing found</p>
            <p className="empty-sub">Try a different search or category</p>
          </div>
        ) : (
          <ul className="projects-list" aria-label="Projects">
            {filtered.map((project) => (
              <li key={project.id}>
                <ProjectCard
                  project={project}
                  onClick={() => onSelectProject(project)}
                />
              </li>
            ))}
          </ul>
        )}
        <div className="list-pad" />
      </main>
    </div>
  );
}
