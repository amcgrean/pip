import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function VendorsPage() {
  const [rows, setRows] = useState<any[]>([])
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ vendor_code: '', vendor_name: '' })
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      const res = await api.get('/vendors')
      setRows(res.data)
    } catch {
      setError('Failed to load vendors')
    }
  }
  useEffect(() => { void load() }, [])

  const save = async () => {
    await api.post('/vendors', form)
    setOpen(false)
    setForm({ vendor_code: '', vendor_name: '' })
    void load()
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between"><Typography variant="h4">Vendors</Typography><Button variant="contained" onClick={() => setOpen(true)}>New Vendor</Button></Stack>
      {error && <Alert severity="error">{error}</Alert>}
      <Table><TableHead><TableRow><TableCell>Code</TableCell><TableCell>Name</TableCell><TableCell>Status</TableCell></TableRow></TableHead>
        <TableBody>{rows.map((r) => <TableRow key={r.id}><TableCell>{r.vendor_code}</TableCell><TableCell>{r.vendor_name}</TableCell><TableCell>{r.is_active ? 'Active' : 'Inactive'}</TableCell></TableRow>)}</TableBody></Table>

      <Dialog open={open} onClose={() => setOpen(false)}><DialogTitle>Create Vendor</DialogTitle><DialogContent><Stack mt={1} spacing={2}><TextField label="Vendor Code" value={form.vendor_code} onChange={(e) => setForm({ ...form, vendor_code: e.target.value })} /><TextField label="Vendor Name" value={form.vendor_name} onChange={(e) => setForm({ ...form, vendor_name: e.target.value })} /></Stack></DialogContent><DialogActions><Button onClick={() => setOpen(false)}>Cancel</Button><Button variant="contained" onClick={() => void save()}>Save</Button></DialogActions></Dialog>
    </Stack>
  )
}
