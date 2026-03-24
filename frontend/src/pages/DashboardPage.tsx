import { Alert, Card, CardContent, Grid, Typography } from '@mui/material'

export function DashboardPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>Operations Dashboard</Typography>
      <Alert severity="info" sx={{ mb: 3 }}>Foundation shell is in place. Module-level widgets and KPIs are the next step.</Alert>
      <Grid container spacing={2}>
        {['Products Workspace', 'Vendor Cross-Reference', 'Import Monitoring'].map((title) => (
          <Grid key={title} size={{ xs: 12, md: 4 }}>
            <Card>
              <CardContent>
                <Typography variant="h6">{title}</Typography>
                <Typography variant="body2" color="text.secondary">Placeholder module card for upcoming operational features.</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  )
}
