# /set-client

**Purpose**: Set the active SDLC Agêntico client profile for the current project.

**Usage**: `/set-client <client-id>`

**Examples**:
```bash
/set-client generic        # Use base framework (default)
/set-client demo-client    # Use demo client profile
/set-client yourco         # Use custom client profile
```

**What it does**:
1. Validates that client profile exists in `.sdlc_clients/` directory
2. Writes client ID to `.project/.client` (persisted)
3. Exports `SDLC_CLIENT` environment variable (current session)
4. Future workflows will use this client's customizations

**Auto-Detection**:
If you don't run `/set-client`, the framework will auto-detect based on:
- Existing `.project/.client` file (from previous session)
- Detection markers in client profiles (file markers, env vars, git remotes)
- Fallback to `generic` (base framework) if no match

**Client Resolution Order**:
1. **Explicit**: User ran `/set-client yourco`
2. **Persisted**: `.project/.client` exists (from previous session)
3. **Auto-Detect**: Matches marker in `.sdlc_clients/*/profile.yml`
4. **Fallback**: Uses `generic` (base framework)

**Related Commands**:
- `/sdlc-start` - Uses active client for workflow
- `/new-feature` - Uses active client for feature
- `/quick-fix` - Uses active client for quick fix

**See Also**:
- `.sdlc_clients/_base/README.md` - How to create client profiles
- `.sdlc_clients/demo-client/` - Example client profile
