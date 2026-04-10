import {
  Accordion, AccordionDetails, AccordionSummary, Alert, Box, Button, Card, CardContent,
  Chip, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Grid, IconButton, MenuItem,
  Paper, Select, Stack, TextField, Typography,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import SearchIcon from '@mui/icons-material/Search'
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward'
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward'
import PublishIcon from '@mui/icons-material/Publish'
import EditIcon from '@mui/icons-material/Edit'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api/client'

interface GuideItem {
  id: number
  product_id: number
  section_name: string | null
  sort_order: number
  override_description: string | null
  internal_sku: string
  normalized_name: string
  display_name: string | null
  thickness: string | null
  width: string | null
  length: string | null
  species_or_material: string | null
  profile: string | null
  finish: string | null
  category_major: string | null
  category_minor: string | null
  primary_image_path: string | null
}

interface Guide {
  id: number
  name: string
  description: string | null
  status: string
  section_order: string[]
  item_count: number
}

export function GuideEditorPage() {
  const { guideId } = useParams<{ guideId: string }>()
  const navigate = useNavigate()
  const [guide, setGuide] = useState<Guide | null>(null)
  const [items, setItems] = useState<GuideItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  // Edit guide name/desc
  const [editOpen, setEditOpen] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDesc, setEditDesc] = useState('')

  // Add product dialog
  const [addOpen, setAddOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const [targetSection, setTargetSection] = useState('')
  const [newSectionName, setNewSectionName] = useState('')

  // Add section dialog
  const [sectionDialogOpen, setSectionDialogOpen] = useState(false)
  const [sectionInput, setSectionInput] = useState('')

  const load = async () => {
    try {
      setLoading(true)
      const res = await api.get(`/guides/${guideId}`)
      setGuide(res.data.guide)
      setItems(res.data.items)
    } catch {
      setError('Failed to load guide')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [guideId])

  // Group items by section
  const sectionOrder = guide?.section_order || []
  const itemsBySection: Record<string, GuideItem[]> = {}
  const unsectionedItems: GuideItem[] = []

  for (const item of items) {
    if (item.section_name) {
      if (!itemsBySection[item.section_name]) itemsBySection[item.section_name] = []
      itemsBySection[item.section_name].push(item)
    } else {
      unsectionedItems.push(item)
    }
  }

  // Ensure all sections from section_order are represented
  for (const s of sectionOrder) {
    if (!itemsBySection[s]) itemsBySection[s] = []
  }

  // Order sections
  const orderedSections = [...sectionOrder]
  for (const s of Object.keys(itemsBySection)) {
    if (!orderedSections.includes(s)) orderedSections.push(s)
  }

  const allSections = [...orderedSections]

  // --- Actions ---
  const updateGuide = async (data: any) => {
    try {
      await api.put(`/guides/${guideId}`, data)
      void load()
    } catch {
      setError('Failed to update guide')
    }
  }

  const handleSaveEdit = async () => {
    await updateGuide({ name: editName, description: editDesc || null })
    setEditOpen(false)
  }

  const toggleStatus = async () => {
    if (!guide) return
    const newStatus = guide.status === 'draft' ? 'published' : 'draft'
    await updateGuide({ status: newStatus })
  }

  const searchProducts = async () => {
    if (!searchQuery.trim()) return
    try {
      setSearching(true)
      const res = await api.get('/products/', { params: { search: searchQuery.trim(), page_size: 20 } })
      setSearchResults(res.data.items)
    } catch {
      setError('Search failed')
    } finally {
      setSearching(false)
    }
  }

  const addProduct = async (productId: number) => {
    const section = targetSection === '__new__' ? newSectionName.trim() : targetSection
    try {
      await api.post(`/guides/${guideId}/items`, {
        product_id: productId,
        section_name: section || null,
        sort_order: 0,
      })
      void load()
      // Remove from search results
      setSearchResults(prev => prev.filter(p => p.id !== productId))
    } catch {
      setError('Failed to add product (may already be in guide)')
    }
  }

  const removeItem = async (itemId: number) => {
    try {
      await api.delete(`/guides/${guideId}/items/${itemId}`)
      void load()
    } catch {
      setError('Failed to remove product')
    }
  }

  const moveItem = async (itemId: number, direction: 'up' | 'down') => {
    const idx = items.findIndex(i => i.id === itemId)
    if (idx < 0) return
    const newItems = [...items]
    const swapIdx = direction === 'up' ? idx - 1 : idx + 1
    if (swapIdx < 0 || swapIdx >= newItems.length) return

    // Swap sort orders
    const temp = newItems[idx].sort_order
    newItems[idx].sort_order = newItems[swapIdx].sort_order
    newItems[swapIdx].sort_order = temp

    try {
      await api.put(`/guides/${guideId}/items/reorder`, {
        items: newItems.map(i => ({ id: i.id, sort_order: i.sort_order, section_name: i.section_name }))
      })
      void load()
    } catch {
      setError('Failed to reorder')
    }
  }

  const handleAddSection = async () => {
    if (!sectionInput.trim() || !guide) return
    const newOrder = [...(guide.section_order || []), sectionInput.trim()]
    await updateGuide({ section_order: newOrder })
    setSectionDialogOpen(false)
    setSectionInput('')
  }

  const removeSection = async (sectionName: string) => {
    if (!guide) return
    const newOrder = (guide.section_order || []).filter(s => s !== sectionName)
    // Move items in this section to unsectioned
    const sectionItems = items.filter(i => i.section_name === sectionName)
    if (sectionItems.length > 0) {
      await api.put(`/guides/${guideId}/items/reorder`, {
        items: sectionItems.map(i => ({ id: i.id, sort_order: i.sort_order, section_name: null }))
      })
    }
    await updateGuide({ section_order: newOrder })
  }

  const downloadPdf = async () => {
    try {
      const res = await api.get(`/guides/${guideId}/pdf`, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `${(guide?.name || 'Guide').replace(/\s+/g, '_')}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      setError('Failed to generate PDF')
    }
  }

  const getDimStr = (item: GuideItem) => {
    const parts = [item.thickness, item.width, item.length].filter(Boolean)
    return parts.length > 0 ? parts.join(' x ') : ''
  }

  if (loading) return <Typography>Loading...</Typography>
  if (!guide) return <Alert severity="error">Guide not found</Alert>

  return (
    <Stack spacing={2.5}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Stack direction="row" spacing={2} alignItems="center">
          <IconButton onClick={() => navigate('/guides')}>
            <ArrowBackIcon />
          </IconButton>
          <Box>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="h4">{guide.name}</Typography>
              <Chip label={guide.status} size="small" color={guide.status === 'published' ? 'success' : 'default'} />
              <IconButton size="small" onClick={() => { setEditName(guide.name); setEditDesc(guide.description || ''); setEditOpen(true) }}>
                <EditIcon fontSize="small" />
              </IconButton>
            </Stack>
            {guide.description && <Typography variant="body2" color="text.secondary">{guide.description}</Typography>}
            <Typography variant="caption" color="text.secondary">{items.length} products in {orderedSections.length} sections</Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<PublishIcon />}
            onClick={toggleStatus}
          >
            {guide.status === 'draft' ? 'Publish' : 'Revert to Draft'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<PictureAsPdfIcon />}
            onClick={downloadPdf}
            disabled={items.length === 0}
          >
            Download PDF
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => { setAddOpen(true); setSearchResults([]); setSearchQuery(''); setTargetSection(allSections[0] || ''); setNewSectionName('') }}
          >
            Add Products
          </Button>
        </Stack>
      </Box>

      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

      {/* Sections */}
      <Grid container spacing={2.5}>
        <Grid size={{ xs: 12 }}>
          <Stack spacing={1.5}>
            {orderedSections.map((sectionName) => (
              <Accordion key={sectionName} defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#f8f9fa' }}>
                  <Stack direction="row" spacing={1} alignItems="center" width="100%">
                    <Typography fontWeight={600}>{sectionName}</Typography>
                    <Chip label={`${(itemsBySection[sectionName] || []).length} items`} size="small" variant="outlined" />
                    <Box flexGrow={1} />
                    <IconButton
                      size="small"
                      color="error"
                      title="Remove section"
                      onClick={(e) => { e.stopPropagation(); void removeSection(sectionName) }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Stack>
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0 }}>
                  {(itemsBySection[sectionName] || []).length === 0 ? (
                    <Box p={3} textAlign="center">
                      <Typography variant="body2" color="text.secondary">No products in this section yet. Click "Add Products" to get started.</Typography>
                    </Box>
                  ) : (
                    <Stack divider={<Divider />}>
                      {(itemsBySection[sectionName] || []).map((item, idx) => (
                        <Box key={item.id} px={2} py={1} display="flex" alignItems="center" gap={2} sx={{ '&:hover': { bgcolor: '#fafafa' } }}>
                          <DragIndicatorIcon fontSize="small" sx={{ color: 'text.disabled' }} />
                          <Box sx={{ width: 48, height: 48, bgcolor: '#f5f5f5', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', flexShrink: 0 }}>
                            {item.primary_image_path ? (
                              <img src={item.primary_image_path} alt="" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'cover' }} />
                            ) : (
                              <Typography variant="caption" color="text.disabled">No img</Typography>
                            )}
                          </Box>
                          <Box sx={{ minWidth: 90 }}>
                            <Typography variant="body2" fontFamily="monospace" color="primary" fontWeight={600} fontSize="0.8rem">{item.internal_sku}</Typography>
                          </Box>
                          <Box flexGrow={1}>
                            <Typography variant="body2" fontWeight={500}>{item.display_name || item.normalized_name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {[item.species_or_material, getDimStr(item), item.profile, item.finish].filter(Boolean).join(' | ')}
                            </Typography>
                          </Box>
                          <Stack direction="row" spacing={0.5}>
                            <IconButton size="small" disabled={idx === 0} onClick={() => moveItem(item.id, 'up')}><ArrowUpwardIcon fontSize="small" /></IconButton>
                            <IconButton size="small" disabled={idx === (itemsBySection[sectionName] || []).length - 1} onClick={() => moveItem(item.id, 'down')}><ArrowDownwardIcon fontSize="small" /></IconButton>
                            <IconButton size="small" color="error" onClick={() => removeItem(item.id)}><DeleteIcon fontSize="small" /></IconButton>
                          </Stack>
                        </Box>
                      ))}
                    </Stack>
                  )}
                </AccordionDetails>
              </Accordion>
            ))}

            {/* Unsectioned items */}
            {unsectionedItems.length > 0 && (
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#fff3e0' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography fontWeight={600} color="warning.main">Unsectioned</Typography>
                    <Chip label={`${unsectionedItems.length} items`} size="small" color="warning" variant="outlined" />
                  </Stack>
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0 }}>
                  <Stack divider={<Divider />}>
                    {unsectionedItems.map((item, idx) => (
                      <Box key={item.id} px={2} py={1} display="flex" alignItems="center" gap={2} sx={{ '&:hover': { bgcolor: '#fafafa' } }}>
                        <DragIndicatorIcon fontSize="small" sx={{ color: 'text.disabled' }} />
                        <Box sx={{ width: 48, height: 48, bgcolor: '#f5f5f5', borderRadius: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', flexShrink: 0 }}>
                          {item.primary_image_path ? (
                            <img src={item.primary_image_path} alt="" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'cover' }} />
                          ) : (
                            <Typography variant="caption" color="text.disabled">No img</Typography>
                          )}
                        </Box>
                        <Box sx={{ minWidth: 90 }}>
                          <Typography variant="body2" fontFamily="monospace" color="primary" fontWeight={600} fontSize="0.8rem">{item.internal_sku}</Typography>
                        </Box>
                        <Box flexGrow={1}>
                          <Typography variant="body2" fontWeight={500}>{item.display_name || item.normalized_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {[item.species_or_material, getDimStr(item), item.profile, item.finish].filter(Boolean).join(' | ')}
                          </Typography>
                        </Box>
                        <IconButton size="small" color="error" onClick={() => removeItem(item.id)}><DeleteIcon fontSize="small" /></IconButton>
                      </Box>
                    ))}
                  </Stack>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Empty state */}
            {items.length === 0 && orderedSections.length === 0 && (
              <Card>
                <CardContent sx={{ py: 6, textAlign: 'center' }}>
                  <MenuBookIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>This guide is empty</Typography>
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    Start by adding a section, then add products from your catalog.
                  </Typography>
                  <Stack direction="row" spacing={1} justifyContent="center">
                    <Button variant="outlined" startIcon={<AddIcon />} onClick={() => setSectionDialogOpen(true)}>Add Section</Button>
                    <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setAddOpen(true); setSearchResults([]); setSearchQuery(''); setTargetSection('') }}>Add Products</Button>
                  </Stack>
                </CardContent>
              </Card>
            )}

            {/* Add section button */}
            {(items.length > 0 || orderedSections.length > 0) && (
              <Button variant="outlined" startIcon={<AddIcon />} onClick={() => setSectionDialogOpen(true)} sx={{ alignSelf: 'flex-start' }}>
                Add Section
              </Button>
            )}
          </Stack>
        </Grid>
      </Grid>

      {/* Add Section Dialog */}
      <Dialog open={sectionDialogOpen} onClose={() => setSectionDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Add Section</DialogTitle>
        <DialogContent>
          <TextField
            label="Section Name"
            fullWidth
            value={sectionInput}
            onChange={(e) => setSectionInput(e.target.value)}
            placeholder="e.g., Casing, Base, Crown"
            autoFocus
            sx={{ mt: 1 }}
            onKeyDown={(e) => { if (e.key === 'Enter') void handleAddSection() }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSectionDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => void handleAddSection()} disabled={!sectionInput.trim()}>Add</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Guide Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Guide</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField label="Guide Name" fullWidth value={editName} onChange={(e) => setEditName(e.target.value)} />
            <TextField label="Description" fullWidth multiline rows={2} value={editDesc} onChange={(e) => setEditDesc(e.target.value)} />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveEdit} disabled={!editName.trim()}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Add Products Dialog */}
      <Dialog open={addOpen} onClose={() => setAddOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Products to Guide</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            {/* Section selector */}
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="body2" fontWeight={500} sx={{ minWidth: 80 }}>Section:</Typography>
              <Select
                size="small"
                value={targetSection}
                onChange={(e) => setTargetSection(e.target.value)}
                sx={{ minWidth: 200 }}
                displayEmpty
              >
                <MenuItem value="">
                  <em>No section (unsectioned)</em>
                </MenuItem>
                {allSections.map(s => (
                  <MenuItem key={s} value={s}>{s}</MenuItem>
                ))}
                <MenuItem value="__new__">
                  <em>+ New Section...</em>
                </MenuItem>
              </Select>
              {targetSection === '__new__' && (
                <TextField
                  size="small"
                  placeholder="New section name"
                  value={newSectionName}
                  onChange={(e) => setNewSectionName(e.target.value)}
                  sx={{ minWidth: 200 }}
                />
              )}
            </Stack>

            {/* Search */}
            <Stack direction="row" spacing={1}>
              <TextField
                size="small"
                fullWidth
                placeholder="Search products by SKU, name, category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') void searchProducts() }}
              />
              <Button variant="contained" onClick={() => void searchProducts()} disabled={searching || !searchQuery.trim()} startIcon={<SearchIcon />}>
                {searching ? 'Searching...' : 'Search'}
              </Button>
            </Stack>

            {/* Results */}
            {searchResults.length > 0 && (
              <Paper variant="outlined" sx={{ maxHeight: 400, overflow: 'auto' }}>
                <Stack divider={<Divider />}>
                  {searchResults.map((p) => {
                    const alreadyAdded = items.some(i => i.product_id === p.id)
                    return (
                      <Box key={p.id} px={2} py={1.5} display="flex" alignItems="center" gap={2} sx={{ '&:hover': { bgcolor: '#fafafa' } }}>
                        <Box flexGrow={1}>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography variant="body2" fontFamily="monospace" color="primary" fontWeight={600} fontSize="0.8rem">{p.internal_sku}</Typography>
                            {p.category_major && <Chip label={p.category_major} size="small" variant="outlined" />}
                          </Stack>
                          <Typography variant="body2">{p.display_name || p.normalized_name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {[p.species_or_material, p.thickness && p.width ? `${p.thickness} x ${p.width}` : null, p.profile].filter(Boolean).join(' | ')}
                          </Typography>
                        </Box>
                        <Button
                          size="small"
                          variant={alreadyAdded ? 'outlined' : 'contained'}
                          disabled={alreadyAdded}
                          onClick={() => void addProduct(p.id)}
                        >
                          {alreadyAdded ? 'Added' : 'Add'}
                        </Button>
                      </Box>
                    )
                  })}
                </Stack>
              </Paper>
            )}

            {searchResults.length === 0 && searchQuery && !searching && (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={3}>
                No products found. Try a different search term.
              </Typography>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddOpen(false)}>Done</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
