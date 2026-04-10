import { Alert, Box, Button, Card, CardContent, Chip, Divider, Stack, Typography } from '@mui/material'
import InfoIcon from '@mui/icons-material/Info'
import StorageIcon from '@mui/icons-material/Storage'
import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { api } from '../api/client'

export function SettingsPage() {
  const { user } = useAuth()
  const [health, setHealth] = useState<any>(null)
  const [version, setVersion] = useState<any>(null)

  useEffect(() => {
    api.get('/health').then((r) => setHealth(r.data)).catch(() => {})
    api.get('/version').then((r) => setVersion(r.data)).catch(() => {})
  }, [])

  return (
    <Stack spacing={2.5}>
      <Box>
        <Typography variant="h4">Settings</Typography>
        <Typography variant="body2" color="text.secondary">System information and configuration</Typography>
      </Box>

      <Card>
        <CardContent>
          <Stack direction="row" spacing={1} alignItems="center" mb={2}>
            <InfoIcon color="primary" />
            <Typography variant="h6">Current User</Typography>
          </Stack>
          <Stack spacing={1}>
            <Typography variant="body2"><strong>Name:</strong> {user?.full_name}</Typography>
            <Typography variant="body2"><strong>Email:</strong> {user?.email}</Typography>
            <Typography variant="body2"><strong>Role:</strong> <Chip label={user?.role} size="small" /></Typography>
          </Stack>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Stack direction="row" spacing={1} alignItems="center" mb={2}>
            <StorageIcon color="primary" />
            <Typography variant="h6">System Status</Typography>
          </Stack>
          {health ? (
            <Stack spacing={1}>
              <Typography variant="body2"><strong>API Status:</strong> <Chip label={health.status} size="small" color="success" /></Typography>
              <Typography variant="body2"><strong>Environment:</strong> {health.environment}</Typography>
              <Typography variant="body2"><strong>Server Time:</strong> {health.utc_time ? new Date(health.utc_time).toLocaleString() : '-'}</Typography>
            </Stack>
          ) : (
            <Alert severity="warning">Unable to reach API health endpoint.</Alert>
          )}

          {version && (
            <Box mt={2}>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2"><strong>App Version:</strong> {version.version}</Typography>
              <Typography variant="body2"><strong>App Name:</strong> {version.name}</Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Stack>
  )
}
