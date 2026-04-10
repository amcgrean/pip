import { Alert, Box, Button, Card, CardContent, Chip, Grid, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material'
import InventoryIcon from '@mui/icons-material/Inventory2'
import LocalShippingIcon from '@mui/icons-material/LocalShipping'
import ImageIcon from '@mui/icons-material/Image'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

const statCards = [
  { key: 'total_active_products', label: 'Active Products', icon: <InventoryIcon sx={{ fontSize: 32, color: 'primary.main' }} />, color: '#e8f5e9' },
  { key: 'total_vendors', label: 'Vendors', icon: <LocalShippingIcon sx={{ fontSize: 32, color: 'secondary.main' }} />, color: '#fff8e1' },
  { key: 'products_with_attachments', label: 'With Attachments', icon: <ImageIcon sx={{ fontSize: 32, color: '#1976d2' }} />, color: '#e3f2fd' },
]

const statusColor: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  completed: 'success',
  completed_with_errors: 'warning',
  processing: 'info',
  failed: 'error',
}

export function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    api.get('/dashboard/summary').then((res) => setSummary(res.data)).catch(() => setError(true))
  }, [])

  if (error) return <Alert severity="error">Failed to load dashboard. Check API connection.</Alert>
  if (!summary) return <Alert severity="info">Loading dashboard...</Alert>

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4">Operations Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">Overview of your product catalog and recent activity</Typography>
      </Box>

      <Grid container spacing={2}>
        {statCards.map((card) => (
          <Grid key={card.key} size={{ xs: 12, sm: 6, md: 4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ width: 56, height: 56, borderRadius: 2, bgcolor: card.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {card.icon}
                </Box>
                <Box>
                  <Typography variant="overline" color="text.secondary">{card.label}</Typography>
                  <Typography variant="h4">{(summary[card.key] ?? 0).toLocaleString()}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Stack direction="row" spacing={2}>
        <Button component={Link} to="/products" variant="contained" endIcon={<ArrowForwardIcon />}>Browse Products</Button>
        <Button component={Link} to="/imports" variant="outlined" endIcon={<UploadFileIcon />}>Import Data</Button>
        <Button component={Link} to="/vendors" variant="outlined" endIcon={<LocalShippingIcon />}>Manage Vendors</Button>
      </Stack>

      {summary.recent_import_jobs?.length > 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Recent Imports</Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>File</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Rows</TableCell>
                  <TableCell align="right">Inserted</TableCell>
                  <TableCell align="right">Updated</TableCell>
                  <TableCell align="right">Errors</TableCell>
                  <TableCell>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {summary.recent_import_jobs.slice(0, 5).map((j: any) => (
                  <TableRow key={j.id}>
                    <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.file_name}</TableCell>
                    <TableCell><Chip label={j.source_type} size="small" variant="outlined" /></TableCell>
                    <TableCell><Chip label={j.status} size="small" color={statusColor[j.status] || 'default'} /></TableCell>
                    <TableCell align="right">{j.total_rows.toLocaleString()}</TableCell>
                    <TableCell align="right">{j.inserted_rows.toLocaleString()}</TableCell>
                    <TableCell align="right">{j.updated_rows.toLocaleString()}</TableCell>
                    <TableCell align="right">{j.error_rows > 0 ? <Typography color="error" variant="body2">{j.error_rows}</Typography> : '0'}</TableCell>
                    <TableCell>{j.created_at ? new Date(j.created_at).toLocaleDateString() : '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </Stack>
  )
}
