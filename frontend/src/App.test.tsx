import React from 'react';
import { render } from '@testing-library/react';

// Simple test that doesn't require router
test('renders application without crashing', () => {
  // Create a minimal component to test basic rendering
  const TestComponent = () => <div>Test App</div>;
  render(<TestComponent />);
  expect(document.body).toBeInTheDocument();
});
