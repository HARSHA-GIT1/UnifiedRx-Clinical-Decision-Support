import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#0F4C5C", // Clinical Deep Teal
      light: "#1B6D82",
      dark: "#09333E",
      contrastText: "#FFFFFF",
    },
    secondary: {
      main: "#2E8B75", // Medical Sage
      light: "#41A68E",
      dark: "#1E6554",
      contrastText: "#FFFFFF",
    },
    ayush: {
      main: "#C07D32", // Warm Ochre / AYUSH Amber
      light: "#D8954E",
      dark: "#9E6020",
      contrastText: "#FFFFFF",
    },
    error: {
      main: "#C53030", // Critical Crimson (Major interactions only)
      light: "#E53E3E",
      dark: "#9B2C2C",
    },
    warning: {
      main: "#C07D32", // Moderate interactions
      light: "#DD6B20",
      dark: "#9C4221",
    },
    info: {
      main: "#0F4C5C",
    },
    success: {
      main: "#2E8B75",
    },
    background: {
      default: "#F6F8FA", // Slate Ground canvas
      paper: "#FFFFFF",
    },
    text: {
      primary: "#1A2230", // Charcoal Slate
      secondary: "#5A677D",
    },
    divider: "#E2E8F0",
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    h1: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 700,
      letterSpacing: "-0.02em",
      color: "#0F4C5C",
    },
    h2: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 700,
      letterSpacing: "-0.015em",
      color: "#0F4C5C",
    },
    h3: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 600,
      letterSpacing: "-0.01em",
      color: "#0F4C5C",
    },
    h4: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 600,
      color: "#1A2230",
    },
    h5: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 600,
      color: "#1A2230",
    },
    h6: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 600,
      color: "#1A2230",
    },
    subtitle1: {
      fontWeight: 500,
      color: "#5A677D",
    },
    body1: {
      color: "#1A2230",
      lineHeight: 1.6,
    },
    body2: {
      color: "#5A677D",
      lineHeight: 1.5,
    },
    button: {
      fontFamily: "'Plus Jakarta Sans', sans-serif",
      fontWeight: 600,
      textTransform: "none",
    },
    mono: {
      fontFamily: "'JetBrains Mono', monospace",
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "8px 20px",
          boxShadow: "none",
          "&:hover": {
            boxShadow: "none",
          },
        },
        containedPrimary: {
          backgroundColor: "#0F4C5C",
          "&:hover": {
            backgroundColor: "#165E71",
          },
        },
        containedSecondary: {
          backgroundColor: "#2E8B75",
          "&:hover": {
            backgroundColor: "#267764",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: "1px solid #E2E8F0",
          boxShadow: "0 1px 3px rgba(15, 76, 92, 0.05)",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "#FFFFFF",
          color: "#1A2230",
          boxShadow: "0 1px 2px rgba(15, 76, 92, 0.06)",
          borderBottom: "1px solid #E2E8F0",
        },
      },
    },
  },
});
