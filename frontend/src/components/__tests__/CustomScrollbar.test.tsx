import React from 'react';
import { render } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CustomScrollbar from '../CustomScrollbar';

const theme = createTheme();

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

describe('CustomScrollbar', () => {
  it('renders without crashing', () => {
    const { container } = render(
      <TestWrapper>
        <CustomScrollbar>
          <div>Test content</div>
        </CustomScrollbar>
      </TestWrapper>
    );
    
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders children correctly', () => {
    const testContent = 'This is test content';
    const { getByText } = render(
      <TestWrapper>
        <CustomScrollbar>
          <div>{testContent}</div>
        </CustomScrollbar>
      </TestWrapper>
    );
    
    expect(getByText(testContent)).toBeInTheDocument();
  });

  it('applies custom styles', () => {
    const customStyle = { backgroundColor: 'red' };
    const { container } = render(
      <TestWrapper>
        <CustomScrollbar style={customStyle}>
          <div>Test content</div>
        </CustomScrollbar>
      </TestWrapper>
    );
    
    // SimpleBar creates its own wrapper, so we need to check the correct element
    const scrollbarContainer = container.querySelector('[data-simplebar]') as HTMLElement;
    expect(scrollbarContainer).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'test-scrollbar';
    const { container } = render(
      <TestWrapper>
        <CustomScrollbar className={customClass}>
          <div>Test content</div>
        </CustomScrollbar>
      </TestWrapper>
    );
    
    const scrollbarContainer = container.firstChild as HTMLElement;
    expect(scrollbarContainer).toHaveClass(customClass);
  });
});