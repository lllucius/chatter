// Debug script to understand the streaming parsing error
// Based on the error: "data: {"ty"... is not valid JSON

// This is what would cause the error
const problematicData = 'data: {"type":"token","content":"hello"}';

console.log('Problematic data:', problematicData);

// What the code is supposed to do (correct approach)
if (problematicData.startsWith('data: ')) {
  const raw = problematicData.slice(6).trim();
  console.log('Extracted raw:', raw);
  try {
    const parsed = JSON.parse(raw);
    console.log('Successfully parsed:', parsed);
  } catch (error) {
    console.log('Error parsing extracted raw:', error.message);
  }
}

// What would cause the error (incorrect approach - parsing the full line)
try {
  const parsedDirect = JSON.parse(problematicData);
  console.log('Direct parse successful:', parsedDirect);
} catch (error) {
  console.log('Direct parse error (this is the bug):', error.message);
}

// Test with the exact error case from logs
const errorCase = 'data: {"ty';
console.log('\nTesting error case:', errorCase);

if (errorCase.startsWith('data: ')) {
  const raw = errorCase.slice(6).trim();
  console.log('Extracted raw from error case:', raw);
  try {
    const parsed = JSON.parse(raw);
    console.log('Successfully parsed error case:', parsed);
  } catch (error) {
    console.log('Error parsing error case (incomplete JSON):', error.message);
  }
}

// Test parsing the full error case (what was happening before)
try {
  const parsedErrorCase = JSON.parse(errorCase);
  console.log('Direct parse error case successful:', parsedErrorCase);
} catch (error) {
  console.log('Direct parse error case (this matches the original error):', error.message);
}