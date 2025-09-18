/// <reference types="vite/client" />
/// <reference types="vitest/globals" />

// JSX types for React 19
declare namespace JSX {
  interface Element extends React.ReactElement<any, any> {}
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
