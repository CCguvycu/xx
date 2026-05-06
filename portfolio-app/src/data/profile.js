/* Edit this file to personalise the app */

export const profile = {
  name: "Your Name",
  tagline: "Builder · Creator · Developer",
  bio: "I build things I want to exist — from Minecraft modpacks to apps. I care about craft, making things that actually work, and shipping them.",
  avatarColor: "#6d5aff", // background color for initials avatar

  stats: [
    { label: "Projects", value: "2+" },
    { label: "Years",    value: "3+" },
    { label: "Released", value: "2"  },
  ],

  /* Fill in any you want displayed. Leave as "" to hide. */
  social: {
    github:  "",   // e.g. "https://github.com/username"
    email:   "",   // e.g. "you@email.com"
    discord: "",   // e.g. "https://discord.gg/invite"
    twitter: "",   // e.g. "https://twitter.com/username"
  },
};

export const skills = [
  {
    category: "Gaming & Modding",
    icon: "🎮",
    items: ["Minecraft Modpacks", "Mod Curation", "Game Design", "CurseForge", "Modrinth"],
  },
  {
    category: "Development",
    icon: "💻",
    items: ["JavaScript", "React", "HTML & CSS", "Node.js", "Vite"],
  },
  {
    category: "Tools & Platforms",
    icon: "🔧",
    items: ["Git", "Android", "Capacitor", "Gradle", "VS Code"],
  },
];
