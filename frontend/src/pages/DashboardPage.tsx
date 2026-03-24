import { Alert, Button, Card, CardContent, Grid, Stack, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export function DashboardPage() {
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    api.get('/dashboard/summary').then((res) => setSummary(res.data)).catch(() => setSummary(null))
  }, [])

  if (!summary) return <Alert severity="info">Loading dashboard...</Alert>

  return (
    <Stack spacing={2}>
      <Typography variant="h4" gutterBottom>Operations Dashboard</Typography>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 3 }}><Card><CardContent><Typography variant="overline">Active Products</Typography><Typography variant="h5">{summary.total_active_products}</Typography></CardContent></Card></Grid>
        <Grid size={{ xs: 12, md: 3 }}><Card><CardContent><Typography variant="overline">Vendors</Typography><Typography variant="h5">{summary.total_vendors}</Typography></CardContent></Card></Grid>
        <Grid size={{ xs: 12, md: 3 }}><Card><CardContent><Typography variant="overline">Products w/ Attachments</Typography><Typography variant="h5">{summary.products_with_attachments}</Typography></CardContent></Card></Grid>
        <Grid size={{ xs: 12, md: 3 }}><Card><CardContent><Typography variant="overline">Recent Imports</Typography><Typography variant="h5">{summary.recent_import_jobs.length}</Typography></CardContent></Card></Grid>
      </Grid>
      <Stack direction="row" spacing={2}><Button component={Link} to="/products" variant="contained">Open Products</Button><Button component={Link} to="/imports" variant="outlined">Open Imports</Button></Stack>
    </Stack>
  )
}
