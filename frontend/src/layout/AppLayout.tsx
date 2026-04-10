import { Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar, AppBar, Typography, Button, Divider, IconButton, useMediaQuery, useTheme } from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import InventoryIcon from '@mui/icons-material/Inventory2'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import LocalShippingIcon from '@mui/icons-material/LocalShipping'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import SettingsIcon from '@mui/icons-material/Settings'
import LogoutIcon from '@mui/icons-material/Logout'
import MenuIcon from '@mui/icons-material/Menu'
import { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const drawerWidth = 250

const navItems = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Products', path: '/products', icon: <InventoryIcon /> },
  { label: 'Guides', path: '/guides', icon: <MenuBookIcon /> },
  { label: 'Vendors', path: '/vendors', icon: <LocalShippingIcon /> },
  { label: 'Imports', path: '/imports', icon: <UploadFileIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
]

export function AppLayout() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [drawerOpen, setDrawerOpen] = useState(false)

  const isActive = (path: string) => path === '/' ? pathname === '/' : pathname.startsWith(path)

  const drawerContent = (
    <>
      <Toolbar />
      <Box sx={{ px: 2, py: 1.5 }}>
        <Typography variant="overline" color="text.secondary">Navigation</Typography>
      </Box>
      <List sx={{ px: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.path}
            component={Link}
            to={item.path}
            selected={isActive(item.path)}
            onClick={() => isMobile && setDrawerOpen(false)}
            sx={{
              borderRadius: 2,
              mb: 0.5,
              '&.Mui-selected': { bgcolor: 'primary.main', color: 'white', '& .MuiListItemIcon-root': { color: 'white' }, '&:hover': { bgcolor: 'primary.dark' } },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: isActive(item.path) ? 600 : 400, fontSize: '0.9rem' }} />
          </ListItemButton>
        ))}
      </List>
      <Divider sx={{ mt: 'auto' }} />
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">PIP v2.0</Typography>
      </Box>
    </>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: 'primary.main' }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setDrawerOpen((prev) => !prev)}
              sx={{ mr: 1 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1 }}>
            <Typography variant="h6" fontWeight={700} letterSpacing={-0.5}>Beisser</Typography>
            <Typography variant="body2" sx={{ opacity: 0.7, mt: 0.3 }}>Internal Operations Platform</Typography>
          </Box>
          <Typography variant="body2" sx={{ mr: 2, opacity: 0.9 }}>{user?.full_name}</Typography>
          <Button color="inherit" size="small" startIcon={<LogoutIcon />} onClick={logout} sx={{ opacity: 0.9 }}>Sign Out</Button>
        </Toolbar>
      </AppBar>

      {isMobile ? (
        <Drawer
          variant="temporary"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{ [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' } }}
        >
          {drawerContent}
        </Drawer>
      ) : (
        <Drawer
          variant="permanent"
          sx={{ width: drawerWidth, [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' } }}
        >
          {drawerContent}
        </Drawer>
      )}

      <Box component="main" sx={{ flexGrow: 1, p: 3, maxWidth: isMobile ? '100vw' : 'calc(100vw - 250px)' }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  )
}
