import * as React from 'react';
import PropTypes from 'prop-types';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import Box from '@mui/material/Box';
import ToggleColorMode from './ToggleColorMode';
import CssBaseline from "@mui/material/CssBaseline";
import {useEffect, useState} from "react";
import {getDesignTokens} from "./theme/themePrimitives.js";

function TemplateFrame({
  children,
}) {
  const [mode, setMode] = useState('light');

  const defaultTheme = createTheme(getDesignTokens(mode));
  // This code only runs on the client side, to determine the system color preference
  useEffect(() => {
    // Check if there is a preferred mode in localStorage
    const savedMode = localStorage.getItem('themeMode');
    if (savedMode) {
      setMode(savedMode);
    } else {
      // If no preference is found, it uses system preference
      const systemPrefersDark = window.matchMedia(
        '(prefers-color-scheme: dark)',
      ).matches;
      setMode(systemPrefersDark ? 'dark' : 'light');
    }
  }, []);

  const toggleColorMode = () => {
    const newMode = mode === 'dark' ? 'light' : 'dark';
    setMode(newMode);
    localStorage.setItem('themeMode', newMode); // Save the selected mode to localStorage
  };

  return (
    <ThemeProvider theme={defaultTheme}>
      <CssBaseline enableColorScheme/>
      <Box sx={{ height: '100dvh', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ right: 15, top: 15, position: 'absolute' }}>
          <ToggleColorMode
            data-screenshot="toggle-mode"
            mode={mode}
            toggleColorMode={toggleColorMode}
          />
        </Box>
        <Box sx={{ flex: '1 1', overflow: 'auto' }}>
          {children}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

TemplateFrame.propTypes = {
  children: PropTypes.node,
};

export default TemplateFrame;
