const { ChatterSDK } = require('./sdk/typescript/dist/index.js');

// Create SDK instance
const sdk = new ChatterSDK({
  basePath: 'http://localhost:8000'
});

console.log('SDK instance created');
console.log('Available workflows methods:', Object.getOwnPropertyNames(sdk.workflows.__proto__));
console.log('Checking specific method:', sdk.workflows.listWorkflowTemplatesApiV1WorkflowsTemplates);

// Try to see what the URL would be
console.log('\nMethod details:');
console.log(sdk.workflows.listWorkflowTemplatesApiV1WorkflowsTemplates.toString());