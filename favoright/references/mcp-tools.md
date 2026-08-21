# Favoright MCP tools

Favoright is a closed-source online service with a remote Streamable HTTP MCP server at `https://favoright.app/mcp`. OAuth-capable clients discover and authenticate automatically; token clients use `Authorization: Bearer fvr_live_...`.

## Scopes

| Scope | Tools |
| --- | --- |
| `music:read` | `favorites_status`, `list_favorites`, `search_favorites`, `recommend_tracks`, `search_catalog` |
| `drafts:write` | `create_playlist_draft`, `get_playlist_draft`, `update_playlist_draft`, `delete_playlist_draft` |

## Read and discovery

### `favorites_status`

Input: `platform`: `apple-music` or `spotify`.

Return: cached favorite count, embedding readiness, last region/storefront, sync status/outcome. It does not sync favorites.

### `list_favorites`

Input: `platform`; optional `limit` (1–100) and `offset` (0+).

Return: a paginated ordered list of cached favorites. Use for browsing, not semantic discovery.

### `search_favorites`

Input: `platform`, non-empty `query`; optional `limit` (1–50), `genres` string array, and `year` object `{ min?, max? }`.

Return: semantic matches from the user's cached favorites with canonical provider metadata. Use for an explicit request such as “find favorites with dream-pop energy.”

### `search_catalog`

Input: `platform`, non-empty `query`; optional `regionId` and `limit` (1–25).

Return: canonical provider catalog matches. Use to find a specifically named track or replace/add a track after a recommendation pass.

### `recommend_tracks`

Only supports `platform: "apple-music"`.

Required input: non-empty `query`, `trackCount` (1–100), and `includeFavorites` boolean. Optional input: `regionId`, `genres`, and `mood`.

Supported moods: `happy`, `dark`, `chill`, `energetic`, `party`, `melancholic`, `calm`, `romantic`, `focus`.

Return: ordered canonical Apple Music references and warnings. Favoright uses up to five semantic favorite seeds, ReccoBeats, then conservative Apple Music catalog resolution. Some candidates can be dropped rather than guessed. For duration requests, ask for a bounded count, then trim returned ordered tracks by `durationMs` to approach the target.

## Playlist drafts

A track reference is:

```json
{
  "platform": "apple-music",
  "resourceKind": "catalog-track",
  "id": "provider-track-id"
}
```

The platform may be `apple-music` or `spotify`; `resourceKind` must be `catalog-track` or `library-track`. Preserve the exact references returned by Favoright.

### `create_playlist_draft`

Input: `platform`, non-empty `title`, and non-empty ordered `tracks`; optional `regionId` and `description`.

Return: a validated/hydrated draft plus an approval URL. Give the URL to the user; never open it yourself.

### `get_playlist_draft`

Input: draft UUID `id`.

Return: an owned draft, including its current `version`, metadata, tracks, status, and approval URL. Retrieve before a follow-up edit when you do not have the current version.

### `update_playlist_draft`

Input: draft UUID `id` and current integer `version`; optional non-empty `title`, `description`, `regionId`, and non-empty replacement `tracks`.

Return: the updated draft with a new version. This uses optimistic concurrency: refresh on `version_conflict` before retrying.

### `delete_playlist_draft`

Input: draft UUID `id`.

Delete only an uncreated Favoright draft. Confirm with the user before this destructive action unless they explicitly asked to delete it.

## Error handling

| Code | Response |
| --- | --- |
| `unauthorized` | Ask the user to authenticate or provide correctly configured credentials. |
| `forbidden` | Explain the missing scope and ask the user to authorize/create a credential with it. |
| `sync_required` | Ask the user to sync favorites in Favoright; do not browse the app yourself. |
| `connection_required` | Ask the user to connect the selected music platform in Favoright. |
| `not_found` | State that the referenced draft or track was unavailable. |
| `version_conflict` | Fetch the current draft and retry with the current version after confirming the desired edit. |
| `provider_unavailable` or `rate_limited` | Explain the temporary provider issue and offer to retry later. |
| `invalid_input` | Correct the input from the user's stated intent; ask only for the missing ambiguity. |
