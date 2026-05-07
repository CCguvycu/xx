import { profile } from "../data/profile";
import { projects } from "../data/projects";
import "./AboutScreen.css";

function Avatar({ name, color }) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  return (
    <div className="avatar" style={{ "--av-color": color }} aria-hidden="true">
      {initials}
    </div>
  );
}

export default function AboutScreen() {
  const released = projects.filter((p) => p.status === "Released").length;
  const stats = [
    { label: "Projects", value: projects.length + "+" },
    { label: "Released", value: released },
    ...profile.stats.filter((s) => s.label !== "Projects" && s.label !== "Released"),
  ];

  return (
    <div className="screen about-screen">
      <header className="screen-header">
        <h1 className="screen-title">About</h1>
      </header>

      <main className="scroll-body about-body">

        {/* Profile card */}
        <div className="profile-card">
          <Avatar name={profile.name} color={profile.avatarColor} />
          <h2 className="profile-name">{profile.name}</h2>
          <p className="profile-tagline">{profile.tagline}</p>
        </div>

        {/* Stats row */}
        <div className="stats-row" role="list" aria-label="Stats">
          {stats.map((s) => (
            <div key={s.label} className="stat-item" role="listitem">
              <span className="stat-value">{s.value}</span>
              <span className="stat-label">{s.label}</span>
            </div>
          ))}
        </div>

        {/* Bio */}
        <section className="about-section">
          <h2 className="section-label">Bio</h2>
          <p className="about-bio">{profile.bio}</p>
        </section>

        {/* Edit hint */}
        <p className="edit-hint" aria-label="Customisation hint">
          Edit <code>src/data/profile.js</code> to update your info
        </p>

        <div className="list-pad" />
      </main>
    </div>
  );
}
