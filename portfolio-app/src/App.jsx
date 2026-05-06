import { useState } from "react";
import HomeScreen from "./screens/HomeScreen";
import ProjectDetail from "./screens/ProjectDetail";
import "./App.css";

export default function App() {
  const [selectedProject, setSelectedProject] = useState(null);

  return (
    <div className="app">
      {selectedProject ? (
        <ProjectDetail
          project={selectedProject}
          onBack={() => setSelectedProject(null)}
        />
      ) : (
        <HomeScreen onSelectProject={setSelectedProject} />
      )}
    </div>
  );
}
