---
name: enable-multi-client
description: Enable multi-client architecture feature (creates .sdlc_clients/ structure)
---

# Enable Multi-Client Command

Enables the multi-client architecture feature flag and creates necessary directory structure.

## Usage

```bash
/enable-multi-client
```

## What it does

1. Creates `.sdlc_clients/` directory structure:
   - `_base/` - Template for new clients
   - `generic/` - Default profile (points to base framework)
   - `demo-client/` - Example customization

2. Updates `.claude/settings.json`:
   ```json
   {
     "feature_flags": {
       "multi_client_architecture": true
     },
     "clients": {
       "enabled": true
     }
   }
   ```

3. Makes `/create-client` and `/set-client` commands available

## After Enabling

- Use `/create-client` to create new client profiles
- Use `/set-client <client-id>` to switch active profile
- Agents will use client-specific overrides when available

## Disabling

To disable, set in `.claude/settings.json`:
```json
{
  "feature_flags": {
    "multi_client_architecture": false
  },
  "clients": {
    "enabled": false
  }
}
```

The `.sdlc_clients/` directory won't be deleted automatically.
