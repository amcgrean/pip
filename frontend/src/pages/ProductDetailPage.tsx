import { Alert, Box, Button, Card, CardContent, Chip, Link, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client'

export function ProductDetailPage() {
  const { productId } = useParams()
  const [data, setData] = useState<any>(null)
  const [noteText, setNoteText] = useState('')
  const [noteType, setNoteType] = useState('general')
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [submittingNote, setSubmittingNote] = useState(false)
  const [uploading, setUploading] = useState(false)

  const load = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await api.get(`/products/${productId}`)
      setData(res.data)
    } catch {
      setError('Failed to load product detail')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [productId])

  const addNote = async () => {
    try {
      setSubmittingNote(true)
      await api.post(`/notes/product/${productId}`, { note_text: noteText, note_type: noteType })
      setNoteText('')
      await load()
    } catch {
      setError('Unable to add note')
    } finally {
      setSubmittingNote(false)
    }
  }

  const uploadAttachment = async () => {
    if (!file) return
    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', file)
      await api.post(`/attachments/product/${productId}`, formData)
      setFile(null)
      await load()
    } catch {
      setError('Unable to upload attachment')
    } finally {
      setUploading(false)
    }
  }

  if (loading && !data) return <Typography>Loading...</Typography>

  return (
    <Stack spacing={2}>
      {error && <Alert severity="error">{error}</Alert>}
      <Typography variant="h4">{data.product.display_name || data.product.normalized_name}</Typography>
      <Card><CardContent>
        <Typography variant="h6">Core Product Info</Typography>
        <Typography>SKU: {data.product.internal_sku}</Typography>
        <Typography>Canonical Name: {data.product.canonical_name || data.product.display_name || data.product.normalized_name}</Typography>
        <Typography>Type: {data.product.product_type || '-'}</Typography>
        <Typography>Category: {data.product.category || data.product.category_major || '-'}</Typography>
        <Typography>Status: <Chip size="small" label={data.product.status} /></Typography>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Aliases</Typography>
        {data.aliases.length === 0 && <Typography color="text.secondary">No aliases loaded.</Typography>}
        {data.aliases.map((a: any) => (
          <Box key={a.id} mb={1} p={1} sx={{ border: '1px solid #ddd', borderRadius: 1 }}>
            <Typography>{a.alias_text}</Typography>
            <Typography variant="caption">{a.alias_type || 'general'} • preferred: {a.is_preferred ? 'yes' : 'no'}</Typography>
          </Box>
        ))}
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Images</Typography>
        {data.images.length === 0 && <Typography color="text.secondary">No images loaded.</Typography>}
        <Table size="small"><TableHead><TableRow><TableCell>Type</TableCell><TableCell>Path/URL</TableCell></TableRow></TableHead>
          <TableBody>{data.images.map((img: any) => <TableRow key={img.id}><TableCell>{img.image_type || '-'}</TableCell><TableCell><Link href={img.storage_path} target="_blank" rel="noreferrer">{img.storage_path}</Link></TableCell></TableRow>)}</TableBody></Table>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Documents</Typography>
        {data.documents.length === 0 && <Typography color="text.secondary">No documents loaded.</Typography>}
        <Table size="small"><TableHead><TableRow><TableCell>Type</TableCell><TableCell>Title</TableCell><TableCell>Location</TableCell></TableRow></TableHead>
          <TableBody>{data.documents.map((d: any) => <TableRow key={d.id}><TableCell>{d.document_type}</TableCell><TableCell>{d.title}</TableCell><TableCell>{d.file_url ? <Link href={d.file_url} target="_blank" rel="noreferrer">Open</Link> : d.attachment_id ? `Attachment #${d.attachment_id}` : '-'}</TableCell></TableRow>)}</TableBody></Table>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Vendor Mappings</Typography>
        <Table size="small"><TableHead><TableRow><TableCell>Vendor</TableCell><TableCell>Vendor SKU</TableCell><TableCell>Primary</TableCell></TableRow></TableHead>
          <TableBody>{data.mappings.map((m: any) => <TableRow key={m.id}><TableCell>{m.vendor_name || '-'}</TableCell><TableCell>{m.vendor_sku}</TableCell><TableCell>{m.is_primary ? 'Yes' : 'No'}</TableCell></TableRow>)}</TableBody></Table>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Attachments</Typography>
        <Stack direction="row" spacing={1}>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <Button variant="contained" disabled={!file || uploading} onClick={() => void uploadAttachment()}>{uploading ? 'Uploading...' : 'Upload'}</Button>
        </Stack>
        <Table size="small"><TableHead><TableRow><TableCell>Name</TableCell><TableCell /></TableRow></TableHead>
          <TableBody>{data.attachments.map((a: any) => <TableRow key={a.id}><TableCell>{a.file_name}</TableCell><TableCell><Button href={`${api.defaults.baseURL}${a.download_url}`} target="_blank">Open</Button></TableCell></TableRow>)}</TableBody></Table>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Notes / History</Typography>
        <Stack direction="row" spacing={1} mb={2}>
          <TextField size="small" label="Type" value={noteType} onChange={(e) => setNoteType(e.target.value)} />
          <TextField size="small" fullWidth label="Add note" value={noteText} onChange={(e) => setNoteText(e.target.value)} />
          <Button variant="contained" disabled={submittingNote || !noteText.trim()} onClick={() => void addNote()}>{submittingNote ? 'Adding...' : 'Add'}</Button>
        </Stack>
        {data.notes.map((n: any) => (
          <Box key={n.id} mb={1} p={1} sx={{ border: '1px solid #ddd', borderRadius: 1 }}>
            <Typography variant="caption">{n.note_type} • {new Date(n.created_at).toLocaleString()}</Typography>
            <Typography>{n.note_text}</Typography>
          </Box>
        ))}
      </CardContent></Card>
    </Stack>
  )
}
