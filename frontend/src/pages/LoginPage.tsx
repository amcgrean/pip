import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material'
import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@beisser-internal.local')
  const [password, setPassword] = useState('ChangeMe123!')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Login failed. Verify credentials and API connectivity.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Stack minHeight="100vh" alignItems="center" justifyContent="center" p={2}>
      <Paper sx={{ p: 4, width: 420, maxWidth: '100%' }}>
        <Typography variant="h5" gutterBottom>Beisser Internal Ops Login</Typography>
        <Typography variant="body2" color="text.secondary" mb={2}>Sign in with your internal account.</Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField label="Email" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth />
            <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth />
            <Button type="submit" variant="contained" disabled={isSubmitting}>{isSubmitting ? 'Signing in...' : 'Sign In'}</Button>
          </Stack>
        </Box>
      </Paper>
    </Stack>
  )
}
