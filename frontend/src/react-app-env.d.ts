/// <reference types="vite/client" />
/// <reference types="vitest/globals" />

// JSX types for React 19
declare namespace JSX {
  interface Element extends React.ReactElement<unknown, string | React.JSXElementConstructor<unknown>> {}
  interface IntrinsicElements {
    [elemName: string]: Record<string, unknown>;
  }
}
