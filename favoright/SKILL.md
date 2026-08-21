---
name: favoright
description: Use Favoright's remote Music Control Protocol (MCP) to inspect a user's favorite music, search provider catalogs, generate deterministic Apple Music playlist candidates, and create or edit playlist drafts. Trigger for `/favoright`, Favoright, favorite music, playlist curation, music-library lookup, or a Favoright MCP connection. Explain OAuth setup or personal API-key setup when requested.
---

# Favoright

Use the configured Favoright MCP server as the sole interface to Favoright. Never open, browse, or control the Favoright web app; do not use browser automation, computer use, or GUI tools against it.

## Connect the MCP

Use the deployment's exact `/mcp` endpoint from the user or Favoright Settings. Prefer OAuth 2.1 with PKCE for an interactive user or an OAuth-capable harness:

```bash
codex mcp add favoright -- https://your-favoright-deployment.example/mcp
codex mcp login favoright
```

Have the user finish email sign-in and consent in their browser. OAuth requests the needed scopes: `music:read` for searches and recommendations; `drafts:write` for draft operations. Do not request, copy, or expose OAuth access or refresh tokens.

For headless CI or a harness without OAuth, explain that the user can create a scoped personal access token in **Settings → Personal access tokens** and configure it as a bearer credential. Its format is `fvr_live_<keyId>_<secret>` and it must never be committed, put in a URL, or printed in logs. The harness must send `Authorization: Bearer <token>` on every request. Prefer a secret store or environment variable such as `FAVORIGHT_MCP_TOKEN`; do not fabricate a harness-specific config format.

For OAuth callback `connection refused`, tell the user to keep the harness open, complete consent promptly, then retry the returned local URL with `127.0.0.1` changed to `localhost`, or vice versa. Revoke OAuth grants in **Settings → Connected apps** and tokens in **Settings → Personal access tokens**.

## Work with the user

Use the tool definitions in [references/mcp-tools.md](references/mcp-tools.md) for exact inputs and outputs.

Before gathering tracks or creating a playlist draft, obtain both missing preferences in one concise question:

1. Desired length: song count or approximate duration.
2. Whether favorites should appear in the finished playlist.

Do not search for candidates or create a draft until both are known. Do not re-ask information already supplied. You may call `favorites_status` first to establish connection, platform, and storefront state.

For a generated playlist, always call `recommend_tracks`; never choose songs from model knowledge and search for them afterward. Pass the user's description as `query`, explicit genres as `genres`, and the nearest supported mood when applicable. Use returned canonical track references directly in `create_playlist_draft`.

Use `search_favorites` or `search_catalog` only for explicit lookup, manual additions, replacements, or targeted edits. Preserve returned titles verbatim; never normalize, shorten, or invent song names.

After saving or updating a draft, give the user the returned approval URL. Tell them to open it themselves in Favoright, review or edit, connect the selected music service if needed, and explicitly create the playlist. MCP never writes directly to Apple Music.

On `version_conflict`, call `get_playlist_draft`, show the user the current state when material, then retry only with the current `version` and their confirmed intended change. Explain `sync_required` or `connection_required` clearly and ask the user to sync or connect the applicable music platform in Favoright themselves.

