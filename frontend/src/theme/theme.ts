import { createTheme } from '@mui/material'

export const appTheme = createTheme({
  palette: {
    primary: { main: '#1f4d3f', light: '#2d6b56', dark: '#153829' },
    secondary: { main: '#8a6d3b', light: '#a58654', dark: '#6b5430' },
    background: { default: '#f4f6f8', paper: '#ffffff' },
    success: { main: '#2e7d32' },
    warning: { main: '#ed6c02' },
    error: { main: '#d32f2f' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 600, fontSize: '1.75rem' },
    h5: { fontWeight: 600, fontSize: '1.4rem' },
    h6: { fontWeight: 600, fontSize: '1.1rem' },
    overline: { fontWeight: 600, letterSpacing: 1.2, fontSize: '0.7rem' },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: { border: '1px solid #e0e0e0', transition: 'box-shadow 0.2s', '&:hover': { boxShadow: '0 2px 8px rgba(0,0,0,0.08)' } },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600 },
        contained: { boxShadow: 'none', '&:hover': { boxShadow: '0 2px 6px rgba(0,0,0,0.15)' } },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 500 } },
    },
    MuiTableHead: {
      styleOverrides: {
        root: { '& .MuiTableCell-head': { fontWeight: 700, backgroundColor: '#f8f9fa', color: '#495057', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: 0.5 } },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: { '&:last-child td': { borderBottom: 0 } },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: { borderRight: '1px solid #e8e8e8', backgroundColor: '#fafbfc' },
      },
    },
  },
})
