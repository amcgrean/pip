import { Alert, Box, Button, Card, CardContent, Chip, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography } from '@mui/material'
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

  const load = async () => {
    try {
      const res = await api.get(`/products/${productId}`)
      setData(res.data)
    } catch {
      setError('Failed to load product detail')
    }
  }

  useEffect(() => {
    void load()
  }, [productId])

  const addNote = async () => {
    await api.post(`/notes/product/${productId}`, { note_text: noteText, note_type: noteType })
    setNoteText('')
    await load()
  }

  const uploadAttachment = async () => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    await api.post(`/attachments/product/${productId}`, formData)
    setFile(null)
    await load()
  }

  if (!data) return <Typography>Loading...</Typography>

  return (
    <Stack spacing={2}>
      {error && <Alert severity="error">{error}</Alert>}
      <Typography variant="h4">{data.product.normalized_name}</Typography>
      <Card><CardContent>
        <Typography variant="h6">Core Product Info</Typography>
        <Typography>SKU: {data.product.internal_sku}</Typography>
        <Typography>Type: {data.product.product_type || '-'}</Typography>
        <Typography>Status: <Chip size="small" label={data.product.status} /></Typography>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Vendor Mappings</Typography>
        <Table size="small"><TableHead><TableRow><TableCell>Vendor</TableCell><TableCell>Vendor SKU</TableCell><TableCell>Primary</TableCell></TableRow></TableHead>
          <TableBody>{data.mappings.map((m: any) => <TableRow key={m.id}><TableCell>{m.vendor_name}</TableCell><TableCell>{m.vendor_sku}</TableCell><TableCell>{m.is_primary ? 'Yes' : 'No'}</TableCell></TableRow>)}</TableBody></Table>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Attachments</Typography>
        <Stack direction="row" spacing={1}>
          <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          <Button variant="contained" onClick={() => void uploadAttachment()}>Upload</Button>
        </Stack>
        <Table size="small"><TableHead><TableRow><TableCell>Name</TableCell><TableCell /></TableRow></TableHead>
          <TableBody>{data.attachments.map((a: any) => <TableRow key={a.id}><TableCell>{a.file_name}</TableCell><TableCell><Button href={`${api.defaults.baseURL}${a.download_url}`} target="_blank">Open</Button></TableCell></TableRow>)}</TableBody></Table>
      </CardContent></Card>

      <Card><CardContent>
        <Typography variant="h6" gutterBottom>Notes / History</Typography>
        <Stack direction="row" spacing={1} mb={2}>
          <TextField size="small" label="Type" value={noteType} onChange={(e) => setNoteType(e.target.value)} />
          <TextField size="small" fullWidth label="Add note" value={noteText} onChange={(e) => setNoteText(e.target.value)} />
          <Button variant="contained" onClick={() => void addNote()}>Add</Button>
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
