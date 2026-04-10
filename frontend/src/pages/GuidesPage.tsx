import {
  Alert, Box, Button, Card, CardContent, Chip, Dialog, DialogActions, DialogContent, DialogTitle,
  IconButton, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  TextField, Typography, Paper,
} from '@mui/material'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

const statusColor: Record<string, 'success' | 'warning' | 'info' | 'default'> = {
  draft: 'default',
  published: 'success',
}

export function GuidesPage() {
  const navigate = useNavigate()
  const [guides, setGuides] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Create dialog
  const [createOpen, setCreateOpen] = useState(false)
  const [newName, setNewName] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [creating, setCreating] = useState(false)

  // Delete dialog
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const load = async () => {
    try {
      const params: any = { page, page_size: 20 }
      if (search.trim()) params.search = search.trim()
      const res = await api.get('/guides/', { params })
      setGuides(res.data.items)
      setTotal(res.data.meta.total)
    } catch {
      setError('Failed to load guides')
    }
  }

  useEffect(() => { void load() }, [page])

  const handleCreate = async () => {
    if (!newName.trim()) return
    try {
      setCreating(true)
      const res = await api.post('/guides/', { name: newName.trim(), description: newDesc.trim() || null })
      setCreateOpen(false)
      setNewName('')
      setNewDesc('')
      navigate(`/guides/${res.data.id}`)
    } catch {
      setError('Failed to create guide')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await api.delete(`/guides/${deleteId}`)
      setDeleteId(null)
      void load()
    } catch {
      setError('Failed to delete guide')
    }
  }

  const downloadPdf = async (id: number, name: string) => {
    try {
      const res = await api.get(`/guides/${id}/pdf`, { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `${name.replace(/\s+/g, '_')}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      setError('Failed to generate PDF')
    }
  }

  return (
    <Stack spacing={2.5}>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="h4">Product Guides</Typography>
          <Typography variant="body2" color="text.secondary">Create product guides and export them as PDF</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)}>
          New Guide
        </Button>
      </Box>

      {error && <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>}

      <Card>
        <CardContent sx={{ pb: '16px !important' }}>
          <Box mb={2}>
            <TextField
              size="small"
              placeholder="Search guides..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') void load() }}
              sx={{ width: 300 }}
            />
          </Box>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Guide Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="center">Status</TableCell>
                  <TableCell align="right">Products</TableCell>
                  <TableCell align="right">Sections</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {guides.map((g) => (
                  <TableRow
                    key={g.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/guides/${g.id}`)}
                  >
                    <TableCell>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <MenuBookIcon fontSize="small" color="primary" />
                        <Typography variant="body2" fontWeight={600}>{g.name}</Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 250, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {g.description || '-'}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip label={g.status} size="small" color={statusColor[g.status] || 'default'} />
                    </TableCell>
                    <TableCell align="right">{g.item_count}</TableCell>
                    <TableCell align="right">{g.section_order?.length || 0}</TableCell>
                    <TableCell>{g.created_at ? new Date(g.created_at).toLocaleDateString() : '-'}</TableCell>
                    <TableCell align="right" onClick={(e) => e.stopPropagation()}>
                      <IconButton
                        size="small"
                        title="Download PDF"
                        onClick={() => downloadPdf(g.id, g.name)}
                        disabled={g.item_count === 0}
                      >
                        <PictureAsPdfIcon fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error" title="Delete" onClick={() => setDeleteId(g.id)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
                {guides.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No guides yet. Create one to get started.</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {total > 20 && (
            <Stack direction="row" justifyContent="center" spacing={1} mt={2}>
              <Button size="small" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
              <Typography variant="body2" sx={{ py: 0.5 }}>Page {page} of {Math.ceil(total / 20)}</Typography>
              <Button size="small" disabled={page >= Math.ceil(total / 20)} onClick={() => setPage(p => p + 1)}>Next</Button>
            </Stack>
          )}
        </CardContent>
      </Card>

      {/* Create dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Guide</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Guide Name"
              fullWidth
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="e.g., Mouldings Guide, Decking Guide"
              autoFocus
            />
            <TextField
              label="Description (optional)"
              fullWidth
              multiline
              rows={2}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Brief description of what this guide covers"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!newName.trim() || creating}>
            {creating ? 'Creating...' : 'Create Guide'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirmation */}
      <Dialog open={deleteId !== null} onClose={() => setDeleteId(null)}>
        <DialogTitle>Delete Guide?</DialogTitle>
        <DialogContent>
          <Typography>This will permanently delete the guide and all its product assignments. This cannot be undone.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteId(null)}>Cancel</Button>
          <Button color="error" variant="contained" onClick={handleDelete}>Delete</Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
