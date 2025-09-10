import React from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ProfileForm from '../src/components/ProfileForm';

// Create a Material UI theme
const theme = createTheme();

// Mock the SDK to return test provider data
const mockSDK = {
  profiles: {
    getAvailableProvidersApiV1ProfilesProvidersAvailable: async () => ({
      providers: {
        openai: {
          name: 'openai',
          display_name: 'OpenAI',
          description: 'OpenAI language models',
          models: [
            { name: 'gpt-4', model_name: 'gpt-4', display_name: 'GPT-4', is_default: true, max_tokens: 8192 },
            { name: 'gpt-4-turbo', model_name: 'gpt-4-turbo', display_name: 'GPT-4 Turbo', is_default: false, max_tokens: 128000 },
            { name: 'gpt-3.5-turbo', model_name: 'gpt-3.5-turbo', display_name: 'GPT-3.5 Turbo', is_default: false, max_tokens: 16385 },
          ]
        },
        anthropic: {
          name: 'anthropic',
          display_name: 'Anthropic',
          description: 'Anthropic Claude models',
          models: [
            { name: 'claude-3-opus', model_name: 'claude-3-opus-20240229', display_name: 'Claude 3 Opus', is_default: false, max_tokens: 200000 },
            { name: 'claude-3-sonnet', model_name: 'claude-3-sonnet-20240229', display_name: 'Claude 3 Sonnet', is_default: true, max_tokens: 200000 },
            { name: 'claude-3-haiku', model_name: 'claude-3-haiku-20240307', display_name: 'Claude 3 Haiku', is_default: false, max_tokens: 200000 },
          ]
        }
      },
      default_provider: 'openai'
    })
  }
};

// Mock the auth service
jest.mock('../src/services/auth-service', () => ({
  getSDK: () => mockSDK
}));

function TestApp() {
  const [formOpen, setFormOpen] = React.useState(true);

  const handleSubmit = async (data) => {
    console.log('Form submitted with data:', data);
    setFormOpen(false);
  };

  const handleClose = () => {
    setFormOpen(false);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div style={{ padding: '20px' }}>
        <h1>ProfileForm Test</h1>
        <button onClick={() => setFormOpen(true)}>Open Form</button>
        <ProfileForm
          open={formOpen}
          mode="create"
          onSubmit={handleSubmit}
          onClose={handleClose}
          initialData={null}
        />
      </div>
    </ThemeProvider>
  );
}

// Mount the test app
const container = document.getElementById('root');
const root = createRoot(container);
root.render(<TestApp />);