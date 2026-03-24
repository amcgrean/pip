import { Box, Drawer, List, ListItemButton, ListItemText, Toolbar, AppBar, Typography, Button } from '@mui/material'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const drawerWidth = 240

const navItems = [
  { label: 'Dashboard', path: '/' },
  { label: 'Products', path: '/products' },
  { label: 'Vendors', path: '/vendors' },
  { label: 'Imports', path: '/imports' },
  { label: 'Settings / Admin', path: '/settings' },
]

export function AppLayout() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography sx={{ flexGrow: 1 }} variant="h6">Beisser Internal Operations</Typography>
          <Typography sx={{ mr: 2 }}>{user?.full_name}</Typography>
          <Button color="inherit" onClick={logout}>Sign Out</Button>
        </Toolbar>
      </AppBar>
      <Drawer variant="permanent" sx={{ width: drawerWidth, [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' } }}>
        <Toolbar />
        <List>
          {navItems.map((item) => (
            <ListItemButton key={item.path} component={Link} to={item.path} selected={pathname === item.path}>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  )
}
