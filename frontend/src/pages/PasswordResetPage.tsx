import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Paper,
  Container,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { Email, VpnKey, CheckCircle } from '@mui/icons-material';
import { useForm } from '../hooks/useForm';
import { getSDK } from '../services/auth-service';
import { toastService } from '../services/toast-service';
import { handleError } from '../utils/error-handler';

interface RequestResetFormValues extends Record<string, unknown> {
  email: string;
}

interface ConfirmResetFormValues extends Record<string, unknown> {
  token: string;
  newPassword: string;
  confirmPassword: string;
}

const PasswordResetPage: React.FC = () => {
  const [step, setStep] = useState<'request' | 'confirm' | 'complete'>(
    'request'
  );
  const [email, setEmail] = useState('');

  const requestForm = useForm<RequestResetFormValues>({
    initialValues: {
      email: '',
    },
    validate: (values) => {
      const errors: Partial<Record<keyof RequestResetFormValues, string>> = {};
      if (!values.email) {
        errors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
        errors.email = 'Invalid email format';
      }
      return errors;
    },
    onSubmit: async (values) => {
      try {
        // TODO: Implement password reset when endpoint is available
        // await getSDK().requestPasswordReset(values.email);
        setEmail(values.email);
        setStep('confirm');
        toastService.success('Password reset instructions sent to your email');
      } catch (error: unknown) {
        handleError(error, {
          source: 'PasswordResetPage.handleSendInstructions',
          operation: 'send password reset instructions',
          additionalData: { email: values.email },
        });
        throw error;
      }
    },
  });

  const confirmForm = useForm<ConfirmResetFormValues>({
    initialValues: {
      token: '',
      newPassword: '',
      confirmPassword: '',
    },
    validate: (values) => {
      const errors: Partial<Record<keyof ConfirmResetFormValues, string>> = {};
      if (!values.token) {
        errors.token = 'Reset token is required';
      }
      if (!values.newPassword) {
        errors.newPassword = 'New password is required';
      } else if (values.newPassword.length < 8) {
        errors.newPassword = 'Password must be at least 8 characters';
      }
      if (values.newPassword !== values.confirmPassword) {
        errors.confirmPassword = 'Passwords do not match';
      }
      return errors;
    },
    onSubmit: async (values) => {
      try {
        await getSDK().auth.confirmPasswordResetApiV1AuthPasswordResetConfirm({
          token: values.token,
          newPassword: values.newPassword,
        });
        setStep('complete');
        toastService.success('Password reset successfully');
      } catch (error: unknown) {
        handleError(error, {
          source: 'PasswordResetPage.handleResetPassword',
          operation: 'reset password',
          additionalData: { token: values.token },
        });
        throw error;
      }
    },
  });

  const steps = ['Request Reset', 'Confirm Reset', 'Complete'];
  const stepIndex = step === 'request' ? 0 : step === 'confirm' ? 1 : 2;

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8, mb: 4 }}>
        <Paper elevation={1} sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              Password Reset
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {step === 'request' &&
                'Enter your email to receive reset instructions'}
              {step === 'confirm' &&
                'Enter the reset token and your new password'}
              {step === 'complete' &&
                'Your password has been successfully reset'}
            </Typography>
          </Box>

          <Stepper activeStep={stepIndex} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {step === 'request' && (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <Email sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6">Request Password Reset</Typography>
                </Box>
                <form onSubmit={requestForm.handleSubmit}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    type="email"
                    value={requestForm.values.email}
                    onChange={(e) =>
                      requestForm.setFieldValue('email', e.target.value)
                    }
                    error={!!requestForm.errors.email}
                    helperText={requestForm.errors.email}
                    sx={{ mb: 3 }}
                    autoFocus
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={requestForm.isSubmitting}
                    startIcon={
                      requestForm.isSubmitting ? (
                        <CircularProgress size={20} />
                      ) : (
                        <Email />
                      )
                    }
                  >
                    {requestForm.isSubmitting
                      ? 'Sending...'
                      : 'Send Reset Instructions'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {step === 'confirm' && (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                  <VpnKey sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h6">Reset Your Password</Typography>
                </Box>
                <Alert severity="info" sx={{ mb: 3 }}>
                  Check your email ({email}) for the reset token and enter it
                  below.
                </Alert>
                <form onSubmit={confirmForm.handleSubmit}>
                  <TextField
                    fullWidth
                    label="Reset Token"
                    value={confirmForm.values.token}
                    onChange={(e) =>
                      confirmForm.setFieldValue('token', e.target.value)
                    }
                    error={!!confirmForm.errors.token}
                    helperText={
                      confirmForm.errors.token ||
                      'Enter the token from your email'
                    }
                    sx={{ mb: 3 }}
                    autoFocus
                  />
                  <TextField
                    fullWidth
                    label="New Password"
                    type="password"
                    value={confirmForm.values.newPassword}
                    onChange={(e) =>
                      confirmForm.setFieldValue('newPassword', e.target.value)
                    }
                    error={!!confirmForm.errors.newPassword}
                    helperText={confirmForm.errors.newPassword}
                    sx={{ mb: 3 }}
                  />
                  <TextField
                    fullWidth
                    label="Confirm New Password"
                    type="password"
                    value={confirmForm.values.confirmPassword}
                    onChange={(e) =>
                      confirmForm.setFieldValue(
                        'confirmPassword',
                        e.target.value
                      )
                    }
                    error={!!confirmForm.errors.confirmPassword}
                    helperText={confirmForm.errors.confirmPassword}
                    sx={{ mb: 3 }}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    disabled={confirmForm.isSubmitting}
                    startIcon={
                      confirmForm.isSubmitting ? (
                        <CircularProgress size={20} />
                      ) : (
                        <VpnKey />
                      )
                    }
                  >
                    {confirmForm.isSubmitting
                      ? 'Resetting...'
                      : 'Reset Password'}
                  </Button>
                </form>
                <Button
                  fullWidth
                  variant="text"
                  onClick={() => setStep('request')}
                  sx={{ mt: 2 }}
                >
                  Back to Request Reset
                </Button>
              </CardContent>
            </Card>
          )}

          {step === 'complete' && (
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <CheckCircle
                  sx={{ fontSize: 64, color: 'success.main', mb: 2 }}
                />
                <Typography variant="h6" gutterBottom>
                  Password Reset Complete
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ mb: 3 }}
                >
                  Your password has been successfully reset. You can now log in
                  with your new password.
                </Typography>
                <Button
                  variant="contained"
                  onClick={() => (window.location.href = '/login')}
                  fullWidth
                >
                  Go to Login
                </Button>
              </CardContent>
            </Card>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default PasswordResetPage;
