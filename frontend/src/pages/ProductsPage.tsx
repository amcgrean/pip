import {
  Alert, Box, Button, Card, CardContent, Chip, Dialog, DialogActions, DialogContent, DialogTitle,
  FormControl, IconButton, InputAdornment, InputLabel, MenuItem, Pagination, Paper, Select,
  Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Tooltip, Typography,
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import AddIcon from '@mui/icons-material/Add'
import FilterListIcon from '@mui/icons-material/FilterList'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import ImageIcon from '@mui/icons-material/Image'
import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api/client'

type Product = {
  id: number; internal_sku: string; normalized_name: string
  category_major?: string; category_minor?: string; product_type?: string
  status: string; attachment_count: number; is_stock_item?: boolean
}
type Vendor = { id: number; vendor_name: string }
type Guide = { id: number; name: string; item_count: number }

const PAGE_SIZE = 20
const emptyForm = { internal_sku: '', normalized_name: '', category_major: '', category_minor: '', product_type: '', status: 'active' }

export function ProductsPage() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<Product[]>([])
  const [vendors, setVendors] = useState<Vendor[]>([])
  const [guides, setGuides] = useState<Guide[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [vendorId, setVendorId] = useState<number | ''>('')
  const [guideId, setGuideId] = useState<number | ''>('')
  const [statusFilter, setStatusFilter] = useState('')
  const [hasAttachments, setHasAttachments] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [openForm, setOpenForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total])

  const load = async (p = page) => {
    try {
      setLoading(true)
      setError(null)
      const [productsRes, vendorRes, guidesRes] = await Promise.all([
        api.get('/products', { params: { page: p, page_size: PAGE_SIZE, search: search || undefined, vendor_id: vendorId || undefined, guide_id: guideId || undefined, status: statusFilter || undefined, has_attachments: hasAttachments === '' ? undefined : hasAttachments === 'yes' } }),
        vendors.length ? Promise.resolve({ data: vendors }) : api.get('/vendors'),
        guides.length ? Promise.resolve({ data: { items: guides } }) : api.get('/guides/', { params: { page_size: 100 } }),
      ])
      setRows(productsRes.data.items)
      setTotal(productsRes.data.meta.total)
      if (!vendors.length) setVendors(vendorRes.data)
      if (!guides.length) setGuides(guidesRes.data.items)
    } catch {
      setError('Unable to load products. Check your connection.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [page])

  const applyFilters = () => { setPage(1); void load(1) }

  const handleSearch = (e: React.KeyboardEvent) => { if (e.key === 'Enter') applyFilters() }

  const saveProduct = async () => {
    try {
      setSaveError(null); setSaving(true)
      const res = await api.post('/products', form)
      setOpenForm(false); setForm(emptyForm)
      navigate(`/products/${res.data.id}`)
    } catch (err: any) {
      setSaveError(err?.response?.data?.detail || 'Unable to create product. Check required fields.')
    } finally { setSaving(false) }
  }

  return (
    <Stack spacing={2.5}>
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography variant="h4">Products</Typography>
          <Typography variant="body2" color="text.secondary">{total.toLocaleString()} products in catalog</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenForm(true)}>New Product</Button>
      </Stack>

      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

      <Card>
        <CardContent sx={{ pb: '12px !important' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5} alignItems="center">
            <TextField
              placeholder="Search SKU, name, description..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleSearch}
              size="small"
              sx={{ minWidth: 280 }}
              slotProps={{ input: { startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment> } }}
            />
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel>Vendor</InputLabel>
              <Select value={vendorId} label="Vendor" onChange={(e) => setVendorId(e.target.value as number | '')}>
                <MenuItem value="">All Vendors</MenuItem>
                {vendors.map((v) => <MenuItem key={v.id} value={v.id}>{v.vendor_name}</MenuItem>)}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 170 }}>
              <InputLabel>Guide</InputLabel>
              <Select value={guideId} label="Guide" onChange={(e) => setGuideId(e.target.value as number | '')}>
                <MenuItem value="">All Guides</MenuItem>
                {guides.map((g) => <MenuItem key={g.id} value={g.id}><MenuBookIcon sx={{ fontSize: 16, mr: 0.5, opacity: 0.6 }} />{g.name} ({g.item_count})</MenuItem>)}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 130 }}>
              <InputLabel>Status</InputLabel>
              <Select value={statusFilter} label="Status" onChange={(e) => setStatusFilter(e.target.value)}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Images</InputLabel>
              <Select value={hasAttachments} label="Images" onChange={(e) => setHasAttachments(e.target.value)}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="yes">Has images</MenuItem>
                <MenuItem value="no">No images</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" startIcon={<FilterListIcon />} onClick={applyFilters}>Filter</Button>
          </Stack>
        </CardContent>
      </Card>

      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>SKU</TableCell>
              <TableCell>Product Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Images</TableCell>
              <TableCell align="center" width={50} />
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id} hover sx={{ cursor: 'pointer', '&:hover': { bgcolor: '#f8faf9' } }} onClick={() => navigate(`/products/${row.id}`)}>
                <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.82rem', fontWeight: 500 }}>{row.internal_sku}</TableCell>
                <TableCell sx={{ maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{row.normalized_name}</TableCell>
                <TableCell>
                  {row.category_major && <Chip label={row.category_major} size="small" variant="outlined" sx={{ mr: 0.5 }} />}
                  {row.category_minor && <Typography variant="caption" color="text.secondary">{row.category_minor}</Typography>}
                </TableCell>
                <TableCell>{row.product_type || '-'}</TableCell>
                <TableCell align="center"><Chip label={row.status} size="small" color={row.status === 'active' ? 'success' : 'default'} /></TableCell>
                <TableCell align="center">{row.attachment_count > 0 ? <Tooltip title={`${row.attachment_count} attachment(s)`}><ImageIcon fontSize="small" color="primary" /></Tooltip> : <Typography variant="caption" color="text.secondary">-</Typography>}</TableCell>
                <TableCell align="center"><IconButton size="small" component={Link} to={`/products/${row.id}`} onClick={(e: React.MouseEvent) => e.stopPropagation()}><OpenInNewIcon fontSize="small" /></IconButton></TableCell>
              </TableRow>
            ))}
            {!loading && rows.length === 0 && (
              <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4 }}><Typography color="text.secondary">No products found matching your filters.</Typography></TableCell></TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {totalPages > 1 && (
        <Box display="flex" justifyContent="center">
          <Pagination page={page} count={totalPages} onChange={(_, v) => setPage(v)} color="primary" shape="rounded" />
        </Box>
      )}

      <Dialog open={openForm} onClose={() => setOpenForm(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Product</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {saveError && <Alert severity="error">{saveError}</Alert>}
            <TextField label="Internal SKU" required value={form.internal_sku} onChange={(e) => setForm({ ...form, internal_sku: e.target.value })} helperText="Unique identifier for this product" />
            <TextField label="Product Name" required value={form.normalized_name} onChange={(e) => setForm({ ...form, normalized_name: e.target.value })} />
            <Stack direction="row" spacing={2}>
              <TextField label="Category Major" fullWidth value={form.category_major} onChange={(e) => setForm({ ...form, category_major: e.target.value })} />
              <TextField label="Category Minor" fullWidth value={form.category_minor} onChange={(e) => setForm({ ...form, category_minor: e.target.value })} />
            </Stack>
            <TextField label="Product Type" value={form.product_type} onChange={(e) => setForm({ ...form, product_type: e.target.value })} />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setOpenForm(false)}>Cancel</Button>
          <Button variant="contained" disabled={saving || !form.internal_sku || !form.normalized_name} onClick={() => void saveProduct()}>{saving ? 'Creating...' : 'Create Product'}</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
