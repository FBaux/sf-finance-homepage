/**
 * portal-files — GBR Portal File API
 *
 * Auth: "user"  →  valid Supabase JWT required (set verify_jwt = true in config.toml)
 * ctx.supabase  →  RLS-scoped to the authenticated user
 *
 * GET  ?action=list       &tab=vertrage&path=subfolder
 * GET  ?action=signed-url &tab=vertrage&path=subfolder&file=name.pdf&expires=3600
 * DELETE ?action=delete   body: { paths: ["vertrage/file.pdf"] }
 */

import { withSupabase } from 'npm:@supabase/server'

const BUCKET      = 'portal-files'
const ALLOWED_TABS = new Set(['vertrage', 'belege', 'social-media', 'trading'])

function validatePath(tab: string, subPath = ''): string {
  if (!ALLOWED_TABS.has(tab)) throw new Error(`Unknown tab: ${tab}`)
  const combined = [tab, subPath].filter(Boolean).join('/')
  if (combined.includes('..'))  throw new Error('Path traversal not allowed')
  return combined
}

Deno.serve(
  withSupabase({ auth: 'user', cors: true }, async (req, ctx) => {
    const url    = new URL(req.url)
    const action = url.searchParams.get('action') ?? 'list'
    const method = req.method.toUpperCase()

    // ── LIST ───────────────────────────────────────────────────────────
    if (action === 'list' && method === 'GET') {
      const tab     = url.searchParams.get('tab') ?? ''
      const subPath = url.searchParams.get('path') ?? ''

      let storagePath: string
      try { storagePath = validatePath(tab, subPath) }
      catch (e: unknown) { return Response.json({ error: (e as Error).message }, { status: 400 }) }

      const { data, error } = await ctx.supabase.storage
        .from(BUCKET)
        .list(storagePath, { sortBy: { column: 'name', order: 'asc' } })

      if (error) return Response.json({ error: error.message }, { status: 500 })

      const items = (data ?? []).filter(i => i.name !== '.keep')
      return Response.json({ items })
    }

    // ── SIGNED URL ────────────────────────────────────────────────────
    if (action === 'signed-url' && method === 'GET') {
      const tab      = url.searchParams.get('tab') ?? ''
      const subPath  = url.searchParams.get('path') ?? ''
      const fileName = url.searchParams.get('file') ?? ''
      const expires  = Math.min(Number(url.searchParams.get('expires') ?? 3600), 3600)

      if (!fileName) return Response.json({ error: 'Missing file parameter' }, { status: 400 })

      let fullPath: string
      try { fullPath = validatePath(tab, [subPath, fileName].filter(Boolean).join('/')) }
      catch (e: unknown) { return Response.json({ error: (e as Error).message }, { status: 400 }) }

      const { data, error } = await ctx.supabase.storage
        .from(BUCKET)
        .createSignedUrl(fullPath, expires)

      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ signedUrl: data.signedUrl, expiresIn: expires })
    }

    // ── DELETE ────────────────────────────────────────────────────────
    if (action === 'delete' && method === 'DELETE') {
      const body  = await req.json().catch(() => null) as { paths?: string[] } | null
      const paths = Array.isArray(body?.paths) ? body.paths : []

      if (!paths.length) return Response.json({ error: 'No paths provided' }, { status: 400 })

      try {
        for (const p of paths) {
          const [tab, ...rest] = p.split('/')
          validatePath(tab, rest.join('/'))
        }
      } catch (e: unknown) { return Response.json({ error: (e as Error).message }, { status: 400 }) }

      const { error } = await ctx.supabase.storage.from(BUCKET).remove(paths)
      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ deleted: paths.length })
    }

    return Response.json({ error: 'Unknown action or method' }, { status: 400 })
  }),
)
