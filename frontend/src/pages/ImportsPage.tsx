import { Alert, Button, Card, CardContent, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function ImportsPage() {
  const [jobs, setJobs] = useState<any[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [summary, setSummary] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    const res = await api.get('/imports/jobs')
    setJobs(res.data.items)
  }

  useEffect(() => { void load() }, [])

  const upload = async () => {
    if (!file) return
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/imports/products-csv', formData)
      setSummary(res.data)
      await load()
    } catch {
      setError('Import failed')
    }
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h4">CSV Imports</Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <Card><CardContent><Stack direction="row" spacing={2}><input type="file" accept=".csv" onChange={(e) => setFile(e.target.files?.[0] || null)} /><Button variant="contained" onClick={() => void upload()}>Upload CSV</Button></Stack>
        {summary && <Alert sx={{ mt: 2 }} severity={summary.errored ? 'warning' : 'success'}>{`Rows: ${summary.total_rows}, Inserted: ${summary.inserted}, Updated: ${summary.updated}, Errors: ${summary.errored}`}</Alert>}
      </CardContent></Card>

      <Table size="small"><TableHead><TableRow><TableCell>File</TableCell><TableCell>Status</TableCell><TableCell>Total</TableCell><TableCell>Inserted</TableCell><TableCell>Updated</TableCell><TableCell>Errors</TableCell></TableRow></TableHead>
        <TableBody>{jobs.map((j) => <TableRow key={j.id}><TableCell>{j.file_name}</TableCell><TableCell>{j.status}</TableCell><TableCell>{j.total_rows}</TableCell><TableCell>{j.inserted_rows}</TableCell><TableCell>{j.updated_rows}</TableCell><TableCell>{j.error_rows}</TableCell></TableRow>)}</TableBody></Table>
    </Stack>
  )
}
