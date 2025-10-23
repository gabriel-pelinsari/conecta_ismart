const theme = {
  // Altere só isso pra rebrand
  colors: {
    bg: "#0B0B0C",          // fundo app (quase preto — “graphite”)
    surface: "#111113",     // cartões/contêiner
    text: "#F5F5F7",        // texto principal
    textMuted: "#B5B8BD",   // texto secundário
    primary: "#0071E3",     // azul suave (lembra Apple)
    outline: "#2C2C2E",     // linhas sutis
    success: "#34C759",
    danger: "#FF3B30",
  },
  fonts: {
    // San Francisco → cair para system fonts
    sans: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif`,
  },
  radii: {
    xs: "6px",
    sm: "10px",
    md: "14px",
    lg: "18px",
  },
  shadows: {
    soft: "0 1px 2px rgba(0,0,0,0.2), 0 10px 30px rgba(0,0,0,0.25)",
    focus: "0 0 0 3px rgba(0,113,227,0.35)",
  },
  sizes: {
    container: "380px",
  }
};

export default theme;
