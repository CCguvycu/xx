import { useState } from "react";
import HomeScreen from "./screens/HomeScreen";
import SkillsScreen from "./screens/SkillsScreen";
import AboutScreen from "./screens/AboutScreen";
import ContactScreen from "./screens/ContactScreen";
import ProjectDetail from "./screens/ProjectDetail";
import BottomNav from "./components/BottomNav";
import "./App.css";

export default function App() {
  const [activeTab, setActiveTab] = useState("projects");
  const [selectedProject, setSelectedProject] = useState(null);

  if (selectedProject) {
    return (
      <div className="app">
        <ProjectDetail
          project={selectedProject}
          onBack={() => setSelectedProject(null)}
        />
      </div>
    );
  }

  return (
    <div className="app">
      <div className="screen-wrap">
        {activeTab === "projects" && (
          <HomeScreen key="projects" onSelectProject={setSelectedProject} />
        )}
        {activeTab === "skills"   && <SkillsScreen  key="skills" />}
        {activeTab === "about"    && <AboutScreen   key="about" />}
        {activeTab === "contact"  && <ContactScreen key="contact" />}
      </div>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}
