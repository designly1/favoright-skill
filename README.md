# Favoright Skill

Use Favoright’s remote MCP to explore a user’s favorite music, generate deterministic Apple Music playlist candidates, and safely create or edit playlist drafts through OAuth or personal API-key authentication.

## Install

Install or copy the [`favoright/`](./favoright) directory into your agent harness’s skills location, then invoke it as `/favoright` (or `$favoright` where that is the harness convention).

## Connect Favoright

Favoright is a remote Streamable HTTP MCP server. Use the exact `/mcp` endpoint shown in the user’s Favoright Settings.

OAuth 2.1 with PKCE is the preferred option for Codex and other OAuth-capable clients:

```bash
codex mcp add favoright -- https://your-favoright-deployment.example/mcp
codex mcp login favoright
```

For headless clients without OAuth support, use a scoped personal access token (`fvr_live_...`) as a bearer token. Keep it in a secret store or environment variable; never commit it, put it in a URL, or include it in logs.

## What it covers

- Favorite-library status, paging, and semantic search
- Apple Music catalog search and deterministic recommendations
- Draft creation, retrieval, optimistic updates, and deletion
- OAuth scopes, token safety, callback recovery, and revocation
- Draft-first behavior: agents return an approval URL; the user reviews and creates the playlist in Favoright

See [`favoright/SKILL.md`](./favoright/SKILL.md) for the agent workflow and [`favoright/references/mcp-tools.md`](./favoright/references/mcp-tools.md) for the complete MCP tool reference.
