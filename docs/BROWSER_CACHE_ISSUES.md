# Browser Cache Issues

## Common Problem: "Function is not defined" Errors

If you encounter errors like:
```
sdk.workflows.exportWorkflowTemplateApiV1WorkflowsTemplatesTemplateIdExport is not a function
```

This typically indicates that your browser has cached an old version of the application JavaScript bundles.

## Solution

### For Users
1. **Hard Refresh** the page:
   - **Chrome/Firefox/Edge (Windows/Linux)**: `Ctrl + Shift + R` or `Ctrl + F5`
   - **Chrome/Firefox/Edge (Mac)**: `Cmd + Shift + R`
   - **Safari**: `Cmd + Option + R`

2. **Clear Browser Cache**:
   - Open browser developer tools (`F12`)
   - Right-click the refresh button
   - Select "Empty Cache and Hard Reload"

3. **Incognito/Private Mode**:
   - Test in an incognito/private window to verify it's a cache issue
   - If it works there, clear your regular browser cache

### For Developers
1. **Restart Development Server**:
   ```bash
   # Stop the frontend dev server (Ctrl+C)
   cd frontend
   npm run dev
   ```

2. **Clear Node Modules Cache** (if needed):
   ```bash
   cd frontend
   rm -rf node_modules/.vite
   npm run dev
   ```

3. **Rebuild SDK** (if you suspect SDK issues):
   ```bash
   # From project root
   python3 scripts/generate_sdks.py --typescript --verbose
   cd sdk/typescript
   npm run build
   cd ../../frontend
   npm install
   ```

4. **Verify SDK is Up-to-Date**:
   ```bash
   # Check that the SDK function exists
   grep -n "exportWorkflowTemplate" sdk/typescript/src/apis/WorkflowsApi.ts
   # Should show the function definition
   ```

## Prevention

### For Development
- Always do a hard refresh when testing new SDK features
- Consider disabling cache in browser dev tools during development
- Use the "Disable cache (while DevTools is open)" setting in Chrome DevTools

### For Production
- Ensure proper cache-busting is configured in the build
- Vite automatically adds content hashes to bundle filenames
- Consider implementing service worker cache invalidation strategies

## Related Files
- Frontend build config: `frontend/vite.config.ts`
- SDK generation: `scripts/generate_sdks.py`
- SDK build: `sdk/typescript/package.json`

## See Also
- [Development Guide](DEVELOPMENT.md#troubleshooting)
- [SDK Generation Guide](sdk-generation.md)
