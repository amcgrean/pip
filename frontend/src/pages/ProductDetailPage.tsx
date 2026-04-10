import { Alert, Box, Button, Card, CardContent, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Grid, IconButton, Link, MenuItem, Paper, Select, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Tooltip, Typography } from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import ImageIcon from '@mui/icons-material/Image'
import UploadFileIcon from '@mui/icons-material/UploadFile'
import OpenInNewIcon from '@mui/icons-material/OpenInNew'
import NoteAddIcon from '@mui/icons-material/NoteAdd'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'

const statusColor: Record<string, 'success' | 'warning' | 'error' | 'default'> = { active: 'success', inactive: 'default' }

export function ProductDetailPage() {
  const { productId } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<any>(null)
  const [noteText, setNoteText] = useState('')
  const [noteType, setNoteType] = useState('general')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [submittingNote, setSubmittingNote] = useState(false)
  const [uploading, setUploading] = useState(false)

  // Add to guide
  const [guideDialogOpen, setGuideDialogOpen] = useState(false)
  const [guides, setGuides] = useState<any[]>([])
  const [selectedGuide, setSelectedGuide] = useState<number | null>(null)
  const [guideSection, setGuideSection] = useState('')

  const loadGuides = async () => {
    try {
      const res = await api.get('/guides/', { params: { page_size: 100 } })
      setGuides(res.data.items)
      if (res.data.items.length > 0) setSelectedGuide(res.data.items[0].id)
    } catch { /* ignore */ }
  }

  const addToGuide = async () => {
    if (!selectedGuide || !productId) return
    try {
      await api.post(`/guides/${selectedGuide}/items`, {
        product_id: parseInt(productId),
        section_name: guideSection.trim() || null,
      })
      setGuideDialogOpen(false)
      setError(null)
    } catch {
      setError('Failed to add to guide (may already be added)')
    }
  }

  const load = async () => {
    try {
      setLoading(true); setError(null)
      const res = await api.get(`/products/${productId}`)
      setData(res.data)
    } catch {
      setError('Failed to load product detail')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [productId])

  const addNote = async () => {
    try {
      setSubmittingNote(true)
      await api.post(`/notes/product/${productId}`, { note_text: noteText, note_type: noteType })
      setNoteText(''); await load()
    } catch { setError('Unable to add note') } finally { setSubmittingNote(false) }
  }

  const uploadAttachment = async () => {
    if (!file) return
    try {
      setUploading(true)
      const fd = new FormData(); fd.append('file', file)
      await api.post(`/attachments/product/${productId}`, fd)
      setFile(null); await load()
    } catch { setError('Unable to upload attachment') } finally { setUploading(false) }
  }

  if (loading && !data) return <Box sx={{ p: 4 }}><Alert severity="info">Loading product...</Alert></Box>
  if (!data) return <Box sx={{ p: 4 }}><Alert severity="error">Product not found or failed to load.</Alert><Button sx={{ mt: 2 }} onClick={() => navigate('/products')}>Back to Products</Button></Box>

  const p = data.product

  return (
    <Stack spacing={2.5}>
      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2}>
        <IconButton onClick={() => navigate('/products')}><ArrowBackIcon /></IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4">{p.display_name || p.normalized_name}</Typography>
          <Stack direction="row" spacing={1} alignItems="center" mt={0.5}>
            <Chip label={p.status} size="small" color={statusColor[p.status] || 'default'} />
            <Typography variant="body2" color="text.secondary" fontFamily="monospace">{p.internal_sku}</Typography>
            {p.is_stock_item && <Chip label="Stock Item" size="small" variant="outlined" color="primary" />}
            {p.category_major && <Chip label={p.category_major} size="small" variant="outlined" />}
          </Stack>
        </Box>
        <Button
          variant="outlined"
          startIcon={<MenuBookIcon />}
          onClick={() => { setGuideDialogOpen(true); void loadGuides() }}
        >
          Add to Guide
        </Button>
      </Stack>

      <Grid container spacing={2.5}>
        {/* Left Column */}
        <Grid size={{ xs: 12, md: 8 }}>
          {/* Product Info */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Product Details</Typography>
              <Grid container spacing={2}>
                {[
                  ['Name', p.normalized_name],
                  ['Canonical', p.canonical_name || p.display_name || '-'],
                  ['Type', p.product_type || '-'],
                  ['Category', [p.category_major, p.category_minor].filter(Boolean).join(' / ') || '-'],
                  ['Species / Material', p.species_or_material || '-'],
                  ['Grade', p.grade || '-'],
                  ['Branch Scope', p.branch_scope || '-'],
                  ['Description', p.description || '-'],
                ].map(([label, value]) => (
                  <Grid key={label as string} size={{ xs: 12, sm: 6 }}>
                    <Typography variant="caption" color="text.secondary" display="block">{label}</Typography>
                    <Typography variant="body2" sx={{ wordBreak: 'break-word' }}>{value}</Typography>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Images */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <ImageIcon color="primary" />
                <Typography variant="h6">Images ({data.images.length})</Typography>
              </Stack>
              {data.images.length === 0 ? (
                <Paper variant="outlined" sx={{ p: 4, textAlign: 'center', bgcolor: '#fafafa' }}>
                  <ImageIcon sx={{ fontSize: 48, color: '#ccc', mb: 1 }} />
                  <Typography color="text.secondary">No images yet. Run the scraper to attach product photos.</Typography>
                </Paper>
              ) : (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                  {data.images.map((img: any) => (
                    <Paper key={img.id} variant="outlined" sx={{ p: 1, textAlign: 'center', width: 190, borderRadius: 2, overflow: 'hidden' }}>
                      {img.storage_path?.startsWith('http') ? (
                        <Box component="img" src={img.storage_path} alt={img.alt_text || ''} sx={{ width: '100%', height: 160, objectFit: 'contain', bgcolor: '#fafafa', borderRadius: 1 }} />
                      ) : (
                        <Box sx={{ width: '100%', height: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f5f5', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary">Local file</Typography>
                        </Box>
                      )}
                      <Typography variant="caption" display="block" mt={0.5} noWrap>{img.alt_text || img.image_type || 'photo'}</Typography>
                      <Link href={img.storage_path} target="_blank" rel="noreferrer" variant="caption">View full size</Link>
                    </Paper>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Vendor Mappings */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Vendor Mappings ({data.mappings.length})</Typography>
              {data.mappings.length === 0 ? (
                <Typography color="text.secondary" variant="body2">No vendor mappings.</Typography>
              ) : (
                <Table size="small">
                  <TableHead><TableRow><TableCell>Vendor</TableCell><TableCell>Vendor SKU</TableCell><TableCell>Description</TableCell><TableCell align="center">Primary</TableCell></TableRow></TableHead>
                  <TableBody>
                    {data.mappings.map((m: any) => (
                      <TableRow key={m.id}>
                        <TableCell sx={{ fontWeight: 500 }}>{m.vendor_name || m.vendor_code || '-'}</TableCell>
                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.82rem' }}>{m.vendor_sku}</TableCell>
                        <TableCell>{m.vendor_description || '-'}</TableCell>
                        <TableCell align="center">{m.is_primary ? <Chip label="Primary" size="small" color="primary" /> : '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column */}
        <Grid size={{ xs: 12, md: 4 }}>
          {/* Aliases */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Aliases ({data.aliases.length})</Typography>
              {data.aliases.length === 0 ? (
                <Typography color="text.secondary" variant="body2">No aliases.</Typography>
              ) : (
                <Stack spacing={1}>
                  {data.aliases.map((a: any) => (
                    <Paper key={a.id} variant="outlined" sx={{ p: 1.5 }}>
                      <Typography variant="body2" fontWeight={500}>{a.alias_text}</Typography>
                      <Typography variant="caption" color="text.secondary">{a.alias_type || 'general'}{a.is_preferred ? ' (preferred)' : ''}</Typography>
                    </Paper>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>

          {/* Documents */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Documents ({data.documents.length})</Typography>
              {data.documents.length === 0 ? (
                <Typography color="text.secondary" variant="body2">No documents.</Typography>
              ) : (
                <Stack spacing={1}>
                  {data.documents.map((d: any) => (
                    <Paper key={d.id} variant="outlined" sx={{ p: 1.5 }}>
                      <Typography variant="body2" fontWeight={500}>{d.title}</Typography>
                      <Typography variant="caption" color="text.secondary">{d.document_type}</Typography>
                      {d.file_url && <Box><Link href={d.file_url} target="_blank" rel="noreferrer" variant="caption">Open</Link></Box>}
                    </Paper>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>

          {/* Attachments */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Attachments ({data.attachments.length})</Typography>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Button variant="outlined" component="label" size="small" startIcon={<UploadFileIcon />}>
                    {file ? file.name : 'Choose File'}
                    <input type="file" hidden onChange={(e) => setFile(e.target.files?.[0] || null)} />
                  </Button>
                  {file && <Button variant="contained" size="small" disabled={uploading} onClick={() => void uploadAttachment()}>{uploading ? 'Uploading...' : 'Upload'}</Button>}
                </Stack>
                {data.attachments.map((a: any) => (
                  <Paper key={a.id} variant="outlined" sx={{ p: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>{a.file_name}</Typography>
                    <Tooltip title="Download">
                      <IconButton size="small" href={`${api.defaults.baseURL}${a.download_url}`} target="_blank"><OpenInNewIcon fontSize="small" /></IconButton>
                    </Tooltip>
                  </Paper>
                ))}
              </Stack>
            </CardContent>
          </Card>

          {/* Notes */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Notes ({data.notes.length})</Typography>
              <Stack spacing={1.5}>
                <Stack direction="row" spacing={1} alignItems="flex-start">
                  <TextField size="small" fullWidth multiline minRows={2} placeholder="Add a note..." value={noteText} onChange={(e) => setNoteText(e.target.value)} />
                </Stack>
                <Stack direction="row" spacing={1}>
                  <TextField size="small" label="Type" value={noteType} onChange={(e) => setNoteType(e.target.value)} sx={{ width: 120 }} />
                  <Button variant="contained" size="small" disabled={submittingNote || !noteText.trim()} startIcon={<NoteAddIcon />} onClick={() => void addNote()}>{submittingNote ? 'Adding...' : 'Add'}</Button>
                </Stack>
                <Divider />
                {data.notes.length === 0 && <Typography color="text.secondary" variant="body2">No notes yet.</Typography>}
                {data.notes.map((n: any) => (
                  <Paper key={n.id} variant="outlined" sx={{ p: 1.5 }}>
                    <Stack direction="row" spacing={1} alignItems="center" mb={0.5}>
                      <Chip label={n.note_type} size="small" variant="outlined" />
                      <Typography variant="caption" color="text.secondary">{new Date(n.created_at).toLocaleString()}</Typography>
                    </Stack>
                    <Typography variant="body2">{n.note_text}</Typography>
                  </Paper>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add to Guide Dialog */}
      <Dialog open={guideDialogOpen} onClose={() => setGuideDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add to Product Guide</DialogTitle>
        <DialogContent>
          {guides.length === 0 ? (
            <Alert severity="info" sx={{ mt: 1 }}>No guides exist yet. Create one from the Guides page first.</Alert>
          ) : (
            <Stack spacing={2} mt={1}>
              <Box>
                <Typography variant="body2" fontWeight={500} mb={0.5}>Select Guide</Typography>
                <Select
                  size="small"
                  fullWidth
                  value={selectedGuide || ''}
                  onChange={(e) => setSelectedGuide(Number(e.target.value))}
                >
                  {guides.map((g: any) => (
                    <MenuItem key={g.id} value={g.id}>{g.name} ({g.item_count} items)</MenuItem>
                  ))}
                </Select>
              </Box>
              <Box>
                <Typography variant="body2" fontWeight={500} mb={0.5}>Section (optional)</Typography>
                <TextField
                  size="small"
                  fullWidth
                  value={guideSection}
                  onChange={(e) => setGuideSection(e.target.value)}
                  placeholder="e.g., Casing, Base, Crown"
                />
                {selectedGuide && guides.find((g: any) => g.id === selectedGuide)?.section_order?.length > 0 && (
                  <Stack direction="row" spacing={0.5} mt={1} flexWrap="wrap" useFlexGap>
                    {guides.find((g: any) => g.id === selectedGuide).section_order.map((s: string) => (
                      <Chip key={s} label={s} size="small" onClick={() => setGuideSection(s)} variant={guideSection === s ? 'filled' : 'outlined'} />
                    ))}
                  </Stack>
                )}
              </Box>
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGuideDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => void addToGuide()} disabled={!selectedGuide || guides.length === 0}>Add to Guide</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
