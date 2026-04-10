import { Alert, Box, Button, Card, CardContent, Chip, Divider, Paper, Stack, Tab, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Tabs, Typography } from '@mui/material'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import DescriptionIcon from '@mui/icons-material/Description'
import TableChartIcon from '@mui/icons-material/TableChart'
import { useEffect, useState } from 'react'
import { api } from '../api/client'

const statusColor: Record<string, 'success' | 'warning' | 'error' | 'info' | 'default'> = {
  completed: 'success', completed_with_errors: 'warning', processing: 'info', failed: 'error', pending: 'default',
}

export function ImportsPage() {
  const [jobs, setJobs] = useState<any[]>([])
  const [tab, setTab] = useState(0)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [xlsxFile, setXlsxFile] = useState<File | null>(null)
  const [summary, setSummary] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  const load = async () => {
    try {
      const res = await api.get('/imports/jobs')
      setJobs(res.data.items)
    } catch { /* ignore */ }
  }

  useEffect(() => { void load() }, [])

  const uploadCsv = async () => {
    if (!csvFile) return
    try {
      setError(null); setUploading(true); setSummary(null)
      const fd = new FormData(); fd.append('file', csvFile)
      const res = await api.post('/imports/products-csv', fd)
      setSummary(res.data); setCsvFile(null); await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'CSV import failed')
    } finally { setUploading(false) }
  }

  const uploadXlsx = async () => {
    if (!xlsxFile) return
    try {
      setError(null); setUploading(true); setSummary(null)
      const fd = new FormData(); fd.append('file', xlsxFile)
      const res = await api.post('/imports/stock-catalog', fd, { timeout: 600000 })
      setSummary(res.data); setXlsxFile(null); await load()
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Stock catalog import failed')
    } finally { setUploading(false) }
  }

  return (
    <Stack spacing={2.5}>
      <Box>
        <Typography variant="h4">Data Imports</Typography>
        <Typography variant="body2" color="text.secondary">Import products, stock catalogs, and vendor data</Typography>
      </Box>

      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}
      {summary && (
        <Alert severity={summary.errored > 0 ? 'warning' : 'success'} onClose={() => setSummary(null)}>
          Import complete: {summary.total_rows?.toLocaleString()} rows processed, {summary.inserted?.toLocaleString()} inserted, {summary.updated?.toLocaleString()} updated{summary.errored > 0 ? `, ${summary.errored} errors` : ''}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
            <Tab icon={<DescriptionIcon />} iconPosition="start" label="Products CSV" />
            <Tab icon={<TableChartIcon />} iconPosition="start" label="Stock Catalog (XLSX)" />
          </Tabs>

          {tab === 0 && (
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">Upload a CSV file with columns: internal_sku, normalized_name, vendor_code, vendor_sku (+ optional fields)</Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Button variant="outlined" component="label" startIcon={<UploadFileIcon />}>
                  {csvFile ? csvFile.name : 'Choose CSV'}
                  <input type="file" hidden accept=".csv" onChange={(e) => setCsvFile(e.target.files?.[0] || null)} />
                </Button>
                {csvFile && <Button variant="contained" disabled={uploading} onClick={() => void uploadCsv()}>{uploading ? 'Importing...' : 'Import CSV'}</Button>}
              </Stack>
            </Stack>
          )}

          {tab === 1 && (
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">Upload the Beisser Stock Catalog XLSX to import all product categories, vendors, and mappings. This may take a few minutes for large catalogs.</Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Button variant="outlined" component="label" startIcon={<UploadFileIcon />}>
                  {xlsxFile ? xlsxFile.name : 'Choose XLSX'}
                  <input type="file" hidden accept=".xlsx" onChange={(e) => setXlsxFile(e.target.files?.[0] || null)} />
                </Button>
                {xlsxFile && <Button variant="contained" disabled={uploading} onClick={() => void uploadXlsx()}>{uploading ? 'Importing (this may take a while)...' : 'Import Stock Catalog'}</Button>}
              </Stack>
            </Stack>
          )}
        </CardContent>
      </Card>

      <Divider />

      <Typography variant="h6">Import History</Typography>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>File</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell align="right">Inserted</TableCell>
              <TableCell align="right">Updated</TableCell>
              <TableCell align="right">Errors</TableCell>
              <TableCell>Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.map((j) => (
              <TableRow key={j.id}>
                <TableCell sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{j.file_name}</TableCell>
                <TableCell><Chip label={j.source_type} size="small" variant="outlined" /></TableCell>
                <TableCell align="center"><Chip label={j.status} size="small" color={statusColor[j.status] || 'default'} /></TableCell>
                <TableCell align="right">{j.total_rows.toLocaleString()}</TableCell>
                <TableCell align="right">{j.inserted_rows.toLocaleString()}</TableCell>
                <TableCell align="right">{j.updated_rows.toLocaleString()}</TableCell>
                <TableCell align="right">{j.error_rows > 0 ? <Typography color="error" variant="body2" fontWeight={600}>{j.error_rows}</Typography> : '0'}</TableCell>
                <TableCell>{j.created_at ? new Date(j.created_at).toLocaleDateString() : '-'}</TableCell>
              </TableRow>
            ))}
            {jobs.length === 0 && (
              <TableRow><TableCell colSpan={8} align="center" sx={{ py: 4 }}><Typography color="text.secondary">No imports yet.</Typography></TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  )
}
