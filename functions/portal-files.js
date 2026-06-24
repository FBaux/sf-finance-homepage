/**
 * Portal Files API
 *
 * Handles secure, server-side file operations for the GBR Portal.
 * Uses RLS-scoped ctx.supabase so each user only reaches their allowed data.
 *
 * Routes (via ?action=<name>):
 *   list        — list files/folders in a storage path
 *   signed-url  — generate a short-lived download URL
 *   delete      — remove one or more files
 *
 * Deploy as a Supabase Edge Function or Cloudflare Worker.
 * All env vars are injected automatically on Supabase Edge Functions;
 * on other runtimes, set them in the platform's secrets manager.
 */

import { withSupabase } from '@supabase/server'

const BUCKET = 'portal-files'

const ALLOWED_TABS = new Set(['vertrage', 'belege', 'social-media', 'trading'])

/** Validate that a storage path stays inside the allowed tab namespace. */
function validatePath(tab, subPath = '') {
  if (!ALLOWED_TABS.has(tab)) {
    throw new Error(`Unknown tab: ${tab}`)
  }
  // Prevent path traversal
  const combined = [tab, subPath].filter(Boolean).join('/')
  if (combined.includes('..')) {
    throw new Error('Path traversal not allowed')
  }
  return combined
}

export default {
  fetch: withSupabase({ auth: 'user', cors: true }, async (req, ctx) => {
    const url    = new URL(req.url)
    const action = url.searchParams.get('action') ?? 'list'
    const method = req.method.toUpperCase()

    // ── LIST files/folders ──────────────────────────────────────────────
    if (action === 'list' && method === 'GET') {
      const tab     = url.searchParams.get('tab') ?? ''
      const subPath = url.searchParams.get('path') ?? ''

      let storagePath
      try { storagePath = validatePath(tab, subPath) }
      catch (e) { return Response.json({ error: e.message }, { status: 400 }) }

      const { data, error } = await ctx.supabase.storage
        .from(BUCKET)
        .list(storagePath, { sortBy: { column: 'name', order: 'asc' } })

      if (error) return Response.json({ error: error.message }, { status: 500 })

      const items = (data ?? []).filter(i => i.name !== '.keep')
      return Response.json({ items })
    }

    // ── SIGNED URL for download/preview ────────────────────────────────
    if (action === 'signed-url' && method === 'GET') {
      const tab       = url.searchParams.get('tab') ?? ''
      const subPath   = url.searchParams.get('path') ?? ''
      const fileName  = url.searchParams.get('file') ?? ''
      const expiresIn = Math.min(Number(url.searchParams.get('expires') ?? 3600), 3600)

      if (!fileName) return Response.json({ error: 'Missing file parameter' }, { status: 400 })

      let fullPath
      try { fullPath = validatePath(tab, [subPath, fileName].filter(Boolean).join('/')) }
      catch (e) { return Response.json({ error: e.message }, { status: 400 }) }

      const { data, error } = await ctx.supabase.storage
        .from(BUCKET)
        .createSignedUrl(fullPath, expiresIn)

      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ signedUrl: data.signedUrl, expiresIn })
    }

    // ── DELETE file(s) ──────────────────────────────────────────────────
    if (action === 'delete' && method === 'DELETE') {
      const body = await req.json().catch(() => null)
      const paths = Array.isArray(body?.paths) ? body.paths : []

      if (!paths.length) return Response.json({ error: 'No paths provided' }, { status: 400 })

      // Validate every path before touching storage
      try {
        for (const p of paths) {
          const [tab, ...rest] = p.split('/')
          validatePath(tab, rest.join('/'))
        }
      } catch (e) { return Response.json({ error: e.message }, { status: 400 }) }

      const { error } = await ctx.supabase.storage.from(BUCKET).remove(paths)
      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ deleted: paths.length })
    }

    // ── UPLOAD (delegates to direct Supabase Storage — handled client-side) ─
    // Server-side upload would stream the multipart body to storage.
    // For file sizes < 50 MB the client-side SDK is sufficient and avoids
    // double-proxying. Add a handler here only if you need server-side
    // virus scanning, size enforcement, or metadata extraction.

    return Response.json({ error: 'Unknown action or method' }, { status: 400 })
  }),
}
