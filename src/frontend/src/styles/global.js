import { createGlobalStyle } from "styled-components";

const GlobalStyle = createGlobalStyle`
  :root {
    color-scheme: dark;
  }

  *, *::before, *::after { box-sizing: border-box; }

  html, body, #root { height: 100%; }
  body {
    margin: 0;
    font-family: ${({ theme }) => theme.fonts.sans};
    background: ${({ theme }) => theme.colors.bg};
    color: ${({ theme }) => theme.colors.text};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    letter-spacing: -0.01em;
  }

  a { color: inherit; text-decoration: none; }

  ::selection {
    background: ${({ theme }) => theme.colors.primary};
    color: white;
  }

  /* Focus visível e elegante */
  :focus-visible {
    outline: none;
    box-shadow: ${({ theme }) => theme.shadows.focus};
    border-radius: 8px;
  }

  /* Inputs base */
  input, button {
    font-family: inherit;
    font-size: 16px;
  }
`;

export default GlobalStyle;
