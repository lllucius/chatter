import React from 'react';
import { ToastContainer } from 'react-toastify';
import { useTheme } from '@mui/material/styles';
import 'react-toastify/dist/ReactToastify.css';

const ThemedToastContainer: React.FC = () => {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const toastStyle = {
    '--toastify-color-light': isDark ? '#1e1e1e' : '#ffffff',
    '--toastify-color-dark': isDark ? '#ffffff' : '#1e1e1e',
    '--toastify-color-info': isDark ? '#2196f3' : '#1976d2',
    '--toastify-color-success': isDark ? '#4caf50' : '#2e7d32',
    '--toastify-color-warning': isDark ? '#ff9800' : '#ed6c02',
    '--toastify-color-error': isDark ? '#f44336' : '#d32f2f',
    '--toastify-color-transparent': 'rgba(255, 255, 255, 0.7)',
    '--toastify-icon-color-info': 'var(--toastify-color-info)',
    '--toastify-icon-color-success': 'var(--toastify-color-success)',
    '--toastify-icon-color-warning': 'var(--toastify-color-warning)',
    '--toastify-icon-color-error': 'var(--toastify-color-error)',
    '--toastify-toast-background': isDark ? '#333333' : '#ffffff',
    '--toastify-toast-width': '320px',
    '--toastify-toast-min-height': '64px',
    '--toastify-toast-max-height': '800px',
    '--toastify-font-family': theme.typography.fontFamily,
    '--toastify-z-index': '9999',
    '--toastify-text-color-light': isDark ? '#ffffff' : '#333333',
    '--toastify-text-color-dark': isDark ? '#333333' : '#ffffff',
    '--toastify-text-color-info': isDark ? '#ffffff' : '#1976d2',
    '--toastify-text-color-success': isDark ? '#ffffff' : '#2e7d32',
    '--toastify-text-color-warning': isDark ? '#000000' : '#ed6c02',
    '--toastify-text-color-error': isDark ? '#ffffff' : '#d32f2f',
    '--toastify-spinner-color': '#616161',
    '--toastify-spinner-color-empty-area': '#e0e0e0',
    '--toastify-color-progress-light': 'linear-gradient(to right, #4caf50, #81c784, #4caf50, #81c784)',
    '--toastify-color-progress-dark': 'linear-gradient(to right, #56d364, #238636, #56d364, #238636)',
    '--toastify-color-progress-info': isDark ? '#2196f3' : '#1976d2',
    '--toastify-color-progress-success': isDark ? '#4caf50' : '#2e7d32',
    '--toastify-color-progress-warning': isDark ? '#ff9800' : '#ed6c02',
    '--toastify-color-progress-error': isDark ? '#f44336' : '#d32f2f',
  } as React.CSSProperties;

  return (
    <div style={toastStyle}>
      <ToastContainer
        position="top-right"
        autoClose={6000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme={isDark ? 'dark' : 'light'}
        limit={3}
        style={{
          fontSize: '14px',
          fontFamily: theme.typography.fontFamily,
        }}
        toastStyle={{
          backgroundColor: isDark ? '#333333' : '#ffffff',
          color: isDark ? '#ffffff' : '#333333',
          border: `1px solid ${isDark ? '#555555' : '#e0e0e0'}`,
          boxShadow: theme.shadows[4],
          borderRadius: theme.shape.borderRadius,
        }}
      />
    </div>
  );
};

export default ThemedToastContainer;