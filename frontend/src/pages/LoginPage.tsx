import React, { useEffect, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { authService } from '../services/auth-service';
import { useForm } from '../hooks/useForm';

interface LoginFormValues {
  username: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();

  const form = useForm<LoginFormValues>({
    initialValues: {
      username: '',
      password: '',
    },
    onSubmit: async (values) => {
      try {
        await authService.login(values.username, values.password);
        navigate('/dashboard');
      } catch (err: any) {
        const errorMessage = err.message || 'Login failed';
        
        // Check if error is related to username (user not found, invalid username format, etc.)
        if (errorMessage.toLowerCase().includes('user') || 
            errorMessage.toLowerCase().includes('username') ||
            errorMessage.toLowerCase().includes('not found')) {
          form.setFieldError('username', errorMessage);
        } else {
          form.setFieldError('password', errorMessage);
        }
        throw err; // Re-throw to stop form submission
      }
    },
    validate: (values) => {
      const errors: Partial<Record<keyof LoginFormValues, string>> = {};
      
      if (!values.username.trim()) {
        errors.username = 'Username is required';
      }
      
      if (!values.password.trim()) {
        errors.password = 'Password is required';
      }
      
      return errors;
    },
  });

  // Redirect if already authenticated
  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography component="h1" variant="h4" sx={{ mb: 3, fontWeight: 'bold', color: 'primary.main' }}>
              Chatter
            </Typography>
            <Typography component="h2" variant="h5" sx={{ mb: 3 }}>
              Sign In
            </Typography>
            
            <Box component="form" onSubmit={form.handleSubmit} sx={{ width: '100%' }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={form.values.username}
                onChange={form.handleChange('username')}
                onBlur={form.handleBlur('username')}
                error={form.touched.username && !!form.errors.username}
                helperText={form.touched.username && form.errors.username}
                disabled={form.isSubmitting}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={form.values.password}
                onChange={form.handleChange('password')}
                onBlur={form.handleBlur('password')}
                error={form.touched.password && !!form.errors.password}
                helperText={form.touched.password && form.errors.password}
                disabled={form.isSubmitting}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, py: 1.5 }}
                disabled={form.isSubmitting || !form.isValid}
              >
                {form.isSubmitting ? <CircularProgress size={24} /> : 'Sign In'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default memo(LoginPage);
