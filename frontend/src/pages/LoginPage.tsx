import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material'
import LockOutlinedIcon from '@mui/icons-material/LockOutlined'
import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null); setIsSubmitting(true)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Login failed. Verify your credentials.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Stack minHeight="100vh" alignItems="center" justifyContent="center" sx={{ bgcolor: '#f4f6f8' }} p={2}>
      <Paper elevation={0} sx={{ p: 5, width: 420, maxWidth: '100%', border: '1px solid #e0e0e0', borderRadius: 3 }}>
        <Stack alignItems="center" mb={3}>
          <Box sx={{ width: 48, height: 48, borderRadius: '50%', bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <LockOutlinedIcon sx={{ color: 'white' }} />
          </Box>
          <Typography variant="h5" fontWeight={700}>Beisser Internal Ops</Typography>
          <Typography variant="body2" color="text.secondary">Sign in to access the operations platform</Typography>
        </Stack>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2.5}>
            <TextField label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth required autoFocus />
            <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth required />
            <Button type="submit" variant="contained" size="large" fullWidth disabled={isSubmitting} sx={{ py: 1.3 }}>{isSubmitting ? 'Signing in...' : 'Sign In'}</Button>
          </Stack>
        </Box>
      </Paper>
    </Stack>
  )
}
