import {
  Alert,
  Box,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  InputLabel,
  MenuItem,
  Pagination,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

type Product = {
  id: number
  internal_sku: string
  normalized_name: string
  category_major?: string
  category_minor?: string
  product_type?: string
  status: string
  attachment_count: number
}

type Vendor = { id: number; vendor_name: string }

const emptyForm = { internal_sku: '', normalized_name: '', category_major: '', category_minor: '', product_type: '', status: 'active' }

export function ProductsPage() {
  const [rows, setRows] = useState<Product[]>([])
  const [vendors, setVendors] = useState<Vendor[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [vendorId, setVendorId] = useState<number | ''>('')
  const [status, setStatus] = useState('')
  const [hasAttachments, setHasAttachments] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [openForm, setOpenForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / 10)), [total])

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const [productsRes, vendorRes] = await Promise.all([
        api.get('/products', {
          params: {
            page,
            page_size: 10,
            search: search || undefined,
            vendor_id: vendorId || undefined,
            status: status || undefined,
            has_attachments: hasAttachments === '' ? undefined : hasAttachments === 'yes',
          },
        }),
        api.get('/vendors'),
      ])
      setRows(productsRes.data.items)
      setTotal(productsRes.data.meta.total)
      setVendors(vendorRes.data)
    } catch {
      setError('Unable to load products')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [page])

  const applyFilters = () => {
    setPage(1)
    void load()
  }

  const saveProduct = async () => {
    try {
      setSaveError(null)
      setSaving(true)
      await api.post('/products', form)
      setOpenForm(false)
      setForm(emptyForm)
      void load()
    } catch {
      setSaveError('Unable to create product. Verify required fields and uniqueness.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Stack spacing={2}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Typography variant="h4">Products Workspace</Typography>
        <Button variant="contained" onClick={() => setOpenForm(true)}>Create Product</Button>
      </Stack>
      {error && <Alert severity="error">{error}</Alert>}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        <TextField label="Search" value={search} onChange={(e) => setSearch(e.target.value)} size="small" />
        <FormControl size="small" sx={{ minWidth: 220 }}>
          <InputLabel>Vendor</InputLabel>
          <Select value={vendorId} label="Vendor" onChange={(e) => setVendorId(e.target.value as number | '')}>
            <MenuItem value="">All</MenuItem>
            {vendors.map((v) => <MenuItem key={v.id} value={v.id}>{v.vendor_name}</MenuItem>)}
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 160 }}>
          <InputLabel>Status</InputLabel>
          <Select value={status} label="Status" onChange={(e) => setStatus(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 180 }}>
          <InputLabel>Attachments</InputLabel>
          <Select value={hasAttachments} label="Attachments" onChange={(e) => setHasAttachments(e.target.value)}>
            <MenuItem value="">All</MenuItem>
            <MenuItem value="yes">Has attachments</MenuItem>
            <MenuItem value="no">No attachments</MenuItem>
          </Select>
        </FormControl>
        <Button variant="outlined" onClick={applyFilters}>Apply</Button>
      </Stack>

      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>SKU</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Attachments</TableCell>
            <TableCell />
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow key={row.id} hover>
              <TableCell>{row.internal_sku}</TableCell>
              <TableCell>{row.normalized_name}</TableCell>
              <TableCell>{row.product_type || '-'}</TableCell>
              <TableCell>{row.category_major || '-'}</TableCell>
              <TableCell><Chip label={row.status} size="small" color={row.status === 'active' ? 'success' : 'default'} /></TableCell>
              <TableCell>{row.attachment_count}</TableCell>
              <TableCell><Button component={Link} to={`/products/${row.id}`}>Open</Button></TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {loading && <Alert severity="info">Loading products...</Alert>}
      {!loading && rows.length === 0 && <Alert severity="info">No products found.</Alert>}
      <Box display="flex" justifyContent="flex-end"><Pagination page={page} count={totalPages} onChange={(_, value) => setPage(value)} /></Box>

      <Dialog open={openForm} onClose={() => setOpenForm(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Product</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {saveError && <Alert severity="error">{saveError}</Alert>}
            <TextField label="Internal SKU" value={form.internal_sku} onChange={(e) => setForm({ ...form, internal_sku: e.target.value })} />
            <TextField label="Normalized Name" value={form.normalized_name} onChange={(e) => setForm({ ...form, normalized_name: e.target.value })} />
            <TextField label="Product Type" value={form.product_type} onChange={(e) => setForm({ ...form, product_type: e.target.value })} />
            <TextField label="Category Major" value={form.category_major} onChange={(e) => setForm({ ...form, category_major: e.target.value })} />
            <TextField label="Category Minor" value={form.category_minor} onChange={(e) => setForm({ ...form, category_minor: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenForm(false)}>Cancel</Button>
          <Button variant="contained" disabled={saving} onClick={() => void saveProduct()}>{saving ? 'Saving...' : 'Save'}</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
