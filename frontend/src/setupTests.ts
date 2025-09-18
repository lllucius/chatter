// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// vi is already available globally through vitest/globals in tsconfig.json

// Mock window.getComputedStyle for SimpleBar compatibility with jsdom
Object.defineProperty(window, 'getComputedStyle', {
  value: (_element: Element) => ({
    getPropertyValue: (prop: string) => {
      if (prop === 'overflow') return 'visible';
      if (prop === 'overflow-x') return 'visible';
      if (prop === 'overflow-y') return 'visible';
      return '';
    },
    // Add other commonly used properties that SimpleBar might need
    overflow: 'visible',
    overflowX: 'visible',
    overflowY: 'visible',
    height: '100px',
    width: '100px',
    paddingLeft: '0px',
    paddingRight: '0px',
    paddingTop: '0px',
    paddingBottom: '0px',
    marginLeft: '0px',
    marginRight: '0px',
    marginTop: '0px',
    marginBottom: '0px',
    borderLeftWidth: '0px',
    borderRightWidth: '0px',
    borderTopWidth: '0px',
    borderBottomWidth: '0px',
  }),
  writable: true,
});
