// Test if the exact streaming parsing logic is working
// This recreates the streaming parsing logic from ChatPage.tsx

function simulateStreamingParsing(streamData) {
  console.log('Testing streaming parsing with:', streamData);
  
  let buffer = '';
  
  for (const chunk of streamData) {
    // Decode the chunk and add to buffer (simulating TextDecoder)
    buffer += chunk;
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // Keep the last incomplete line in buffer

    // Process each complete line
    for (const line of lines) {
      console.log('Processing line:', JSON.stringify(line));
      
      if (line.startsWith('data: ')) {
        const raw = line.slice(6).trim();
        console.log('Extracted raw:', JSON.stringify(raw));

        // Handle special cases
        if (raw === '[DONE]') {
          console.log('End of stream marker found');
          continue;
        }

        try {
          const eventData = JSON.parse(raw);
          console.log('Successfully parsed event:', eventData);
        } catch (error) {
          console.log('Failed to parse as JSON:', error.message);
          console.log('Raw data was:', JSON.stringify(raw));
        }
      } else if (line.trim()) {
        console.log('Ignoring non-data line:', JSON.stringify(line));
      }
    }
  }
  
  if (buffer.trim()) {
    console.log('Remaining buffer after processing:', JSON.stringify(buffer));
  }
}

// Test with normal data
console.log('=== TEST 1: Normal streaming ===');
simulateStreamingParsing([
  'data: {"type":"start","conversation_id":"123"}\n\n',
  'data: {"type":"token","content":"Hello"}\n\n',
  'data: {"type":"token","content":" world"}\n\n',
  'data: {"type":"complete","metadata":{"tokens":2}}\n\n',
  'data: [DONE]\n\n'
]);

// Test with partial/incomplete data that might cause the error
console.log('\n=== TEST 2: Incomplete data ===');
simulateStreamingParsing([
  'data: {"type":"start","conversation_id":"123"}\n\n',
  'data: {"ty', // Incomplete JSON
  'pe":"token","content":"Hello"}\n\n',
]);

// Test with problematic data that would cause the original error
console.log('\n=== TEST 3: Problematic case (what causes the error) ===');
// This simulates what happens if code tries to parse the full line instead of raw
const problematicLine = 'data: {"type":"token","content":"hello"}';
try {
  const wrongResult = JSON.parse(problematicLine); // This would fail
  console.log('Wrong parsing succeeded (unexpected):', wrongResult);
} catch (error) {
  console.log('Wrong parsing failed as expected:', error.message);
}

// But the correct parsing should work
if (problematicLine.startsWith('data: ')) {
  const raw = problematicLine.slice(6).trim();
  try {
    const correctResult = JSON.parse(raw);
    console.log('Correct parsing succeeded:', correctResult);
  } catch (error) {
    console.log('Correct parsing failed (unexpected):', error.message);
  }
}