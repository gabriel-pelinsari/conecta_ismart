import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { ThemeProvider } from "styled-components";
import GlobalStyle from "./styles/global";
import themes, { DEFAULT_THEME } from "./styles/theme";

const getInitialTheme = () => {
  if (typeof window === "undefined") {
    return DEFAULT_THEME;
  }

  const stored = window.localStorage.getItem("theme");
  if (stored && themes[stored]) {
    return stored;
  }

  const prefersLight = window.matchMedia?.("(prefers-color-scheme: light)")?.matches;
  if (prefersLight) {
    return "light";
  }

  return DEFAULT_THEME;
};

function Root() {
  const [themeName, setThemeName] = useState(getInitialTheme);

  useEffect(() => {
    window.localStorage.setItem("theme", themeName);
    document.documentElement.dataset.theme = themeName;
  }, [themeName]);

  const toggleTheme = () => {
    setThemeName((current) => (current === "light" ? "dark" : "light"));
  };

  const currentTheme = themes[themeName] ?? themes[DEFAULT_THEME];

  return (
    <ThemeProvider theme={currentTheme}>
      <GlobalStyle />
      <App themeName={themeName} toggleTheme={toggleTheme} />
    </ThemeProvider>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
);
