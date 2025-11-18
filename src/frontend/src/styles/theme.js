const sharedScales = {
  fonts: {
    sans: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif`,
  },
  radii: {
    xs: "6px",
    sm: "10px",
    md: "14px",
    lg: "18px",
  },
  shadows: {
    soft: "0 12px 30px rgba(15, 23, 42, 0.06)",
    focus: "0 0 0 3px rgba(0,113,227,0.35)",
  },
  sizes: {
    containerSmall: "380px",
    containerMedium: "900px",
    containerLarge: "1200px",
    containerWidthDesktop: "75%",
    containerWidthMobile: "90%",
  },
  breakpoints: {
    mobile: "480px",
    tablet: "768px",
    desktop: "1024px",
    wide: "1440px",
  },
};

const themes = {
  dark: {
    ...sharedScales,
    scheme: "dark",
    colors: {
      bg: "#0B0B0C",
      surface: "#111113",
      text: "#F5F5F7",
      textMuted: "#B5B8BD",
      primary: "#0071E3",
      outline: "#2C2C2E",
      success: "#34C759",
      danger: "#FF3B30",
    },
  },
  light: {
    ...sharedScales,
    scheme: "light",
    colors: {
      bg: "#F6F7FB",
      surface: "#FFFFFF",
      text: "#1C1C1E",
      textMuted: "#5F6268",
      primary: "#0071E3",
      outline: "#D7DAE5",
      success: "#2F9C5D",
      danger: "#D62E2E",
    },
  },
};

export const DEFAULT_THEME = "dark";

export default themes;
