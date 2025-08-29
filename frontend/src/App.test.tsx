import React from 'react';
import { render } from '@testing-library/react';

test('App component exists and is importable', () => {
  // Basic smoke test - just ensure App can be imported
  const App = require('./App').default;
  expect(App).toBeDefined();
  expect(typeof App).toBe('function');
});
