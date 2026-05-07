import { skills } from "../data/profile";
import "./SkillsScreen.css";

export default function SkillsScreen() {
  return (
    <div className="screen skills-screen">
      <header className="screen-header">
        <h1 className="screen-title">Skills</h1>
        <p className="screen-sub">What I work with</p>
      </header>

      <main className="scroll-body skills-body">
        {skills.map((group) => (
          <section key={group.category} className="skill-group">
            <div className="skill-group-head">
              <span className="skill-group-icon" aria-hidden="true">{group.icon}</span>
              <h2 className="skill-group-name">{group.category}</h2>
            </div>
            <ul className="skill-chips" aria-label={`${group.category} skills`}>
              {group.items.map((item) => (
                <li key={item}>
                  <span className="skill-chip">{item}</span>
                </li>
              ))}
            </ul>
          </section>
        ))}
        <div className="list-pad" />
      </main>
    </div>
  );
}
