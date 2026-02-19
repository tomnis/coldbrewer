export interface Theme {
  name: string;
  id: string;
  colors: {
    primary: string;
    primaryGlow: string;
    bg: string;
    bgSecondary: string;
    border: string;
    inputPlaceholder: string;
  };
}

export const themes: Theme[] = [
  {
    name: "Classic Green",
    id: "green",
    colors: {
      primary: "#33ff33",
      primaryGlow: "#33ff33",
      bg: "#1a1a1a",
      bgSecondary: "#0a0a0a",
      border: "#33ff33",
      inputPlaceholder: "#1a5c1a",
    },
  },
  {
    name: "Amber CRT",
    id: "amber",
    colors: {
      primary: "#ffb000",
      primaryGlow: "#ffb000",
      bg: "#1a1208",
      bgSecondary: "#0f0a04",
      border: "#ffb000",
      inputPlaceholder: "#4a3500",
    },
  },
  {
    name: "Blue Terminal",
    id: "blue",
    colors: {
      primary: "#00ffff",
      primaryGlow: "#00ffff",
      bg: "#001a1a",
      bgSecondary: "#000f0f",
      border: "#00ffff",
      inputPlaceholder: "#004d4d",
    },
  },
  {
    name: "Tokyo Cyberpunk",
    id: "pink",
    colors: {
      primary: "#9d00ff",
      primaryGlow: "#00fff7",
      bg: "#0a0612",
      bgSecondary: "#050208",
      border: "#00fff7",
      inputPlaceholder: "#2d1a3d",
    },
  },
  {
    name: "Monochrome",
    id: "mono",
    colors: {
      primary: "#ffffff",
      primaryGlow: "#ffffff",
      bg: "#000000",
      bgSecondary: "#0a0a0a",
      border: "#ffffff",
      inputPlaceholder: "#333333",
    },
  },
  {
    name: "Simple",
    id: "simple",
    colors: {
      primary: "#333333",
      primaryGlow: "#333333",
      bg: "#e8e8e8",
      bgSecondary: "#dcdcdc",
      border: "#555555",
      inputPlaceholder: "#999999",
    },
  },
  {
    name: "Blue-ish",
    id: "blueish",
    colors: {
      primary: "#cccccc",
      primaryGlow: "#cccccc",
      bg: "#454b69",
      bgSecondary: "#363b52",
      border: "#5a6183",
      inputPlaceholder: "#ffcb6b",
    },
  },
];

export const defaultTheme = themes[0];
