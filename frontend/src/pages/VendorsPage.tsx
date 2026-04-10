import { Alert, Box, Button, Card, CardContent, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Typography } from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import LocalShippingIcon from '@mui/icons-material/LocalShipping'
import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Vendor = { id: number; vendor_code: string; vendor_name: string; is_active: boolean }

export function VendorsPage() {
  const [rows, setRows] = useState<Vendor[]>([])
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ vendor_code: '', vendor_name: '' })
  const [error, setError] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

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
    try {
      setSaveError(null); setSaving(true)
      await api.post('/vendors', form)
      setOpen(false); setForm({ vendor_code: '', vendor_name: '' })
      void load()
    } catch (err: any) {
      setSaveError(err?.response?.data?.detail || 'Unable to create vendor.')
    } finally { setSaving(false) }
  }

  return (
    <Stack spacing={2.5}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4">Vendors</Typography>
          <Typography variant="body2" color="text.secondary">{rows.length} suppliers in system</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpen(true)}>New Vendor</Button>
      </Stack>

      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Code</TableCell>
              <TableCell>Vendor Name</TableCell>
              <TableCell align="center">Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((r) => (
              <TableRow key={r.id} hover>
                <TableCell sx={{ fontFamily: 'monospace', fontWeight: 500, fontSize: '0.82rem' }}>{r.vendor_code}</TableCell>
                <TableCell>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <LocalShippingIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                    <Typography variant="body2">{r.vendor_name}</Typography>
                  </Stack>
                </TableCell>
                <TableCell align="center"><Chip label={r.is_active ? 'Active' : 'Inactive'} size="small" color={r.is_active ? 'success' : 'default'} /></TableCell>
              </TableRow>
            ))}
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={3} align="center" sx={{ py: 4 }}><Typography color="text.secondary">No vendors found.</Typography></TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Vendor</DialogTitle>
        <DialogContent>
          <Stack mt={1} spacing={2}>
            {saveError && <Alert severity="error">{saveError}</Alert>}
            <TextField label="Vendor Code" required value={form.vendor_code} onChange={(e) => setForm({ ...form, vendor_code: e.target.value })} helperText="Unique identifier (e.g., FER1000)" />
            <TextField label="Vendor Name" required value={form.vendor_name} onChange={(e) => setForm({ ...form, vendor_name: e.target.value })} helperText="Full company name" />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" disabled={saving || !form.vendor_code || !form.vendor_name} onClick={() => void save()}>{saving ? 'Creating...' : 'Create Vendor'}</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
