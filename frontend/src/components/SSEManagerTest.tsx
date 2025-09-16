import React from 'react';
import { useSSE } from '../services/sse-context';

const SSEManagerTest: React.FC = () => {
  const { manager, isConnected } = useSSE();
  
  return (
    <div style={{ padding: '20px' }}>
      <h1>SSE Manager Test</h1>
      <p>Manager available: {manager ? 'YES' : 'NO'}</p>
      <p>Manager type: {manager ? typeof manager : 'undefined'}</p>
      <p>Is connected: {isConnected ? 'YES' : 'NO'}</p>
      {manager && (
        <div>
          <p>Manager methods available:</p>
          <ul>
            <li>connect: {typeof manager.connect}</li>
            <li>disconnect: {typeof manager.disconnect}</li>
            <li>addEventListener: {typeof manager.addEventListener}</li>
            <li>removeEventListener: {typeof manager.removeEventListener}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default SSEManagerTest;