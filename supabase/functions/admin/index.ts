/**
 * admin — GBR Portal Admin API
 *
 * Auth: "secret"  →  SUPABASE_SECRET_KEY required (never exposed to browser)
 * ctx.supabaseAdmin  →  bypasses RLS (service role)
 * verify_jwt = false in config.toml — @supabase/server validates the secret key itself
 *
 * GET    ?action=list-users
 * POST   ?action=invite-user   body: { email, password }
 * DELETE ?action=remove-user   body: { userId }
 */

import { withSupabase } from 'npm:@supabase/server'

Deno.serve(
  withSupabase({ auth: 'secret', cors: false }, async (req, ctx) => {
    const url    = new URL(req.url)
    const action = url.searchParams.get('action') ?? ''
    const method = req.method.toUpperCase()

    // ── LIST USERS ────────────────────────────────────────────────────
    if (action === 'list-users' && method === 'GET') {
      const { data, error } = await ctx.supabaseAdmin.auth.admin.listUsers()
      if (error) return Response.json({ error: error.message }, { status: 500 })

      const users = data.users.map(u => ({
        id:              u.id,
        email:           u.email,
        created_at:      u.created_at,
        last_sign_in_at: u.last_sign_in_at,
      }))
      return Response.json({ users })
    }

    // ── INVITE USER ───────────────────────────────────────────────────
    if (action === 'invite-user' && method === 'POST') {
      const body = await req.json().catch(() => null) as { email?: string; password?: string } | null
      const { email, password } = body ?? {}

      if (!email || !password) {
        return Response.json({ error: 'email and password are required' }, { status: 400 })
      }

      const { data, error } = await ctx.supabaseAdmin.auth.admin.createUser({
        email,
        password,
        email_confirm: true,
      })

      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ id: data.user.id, email: data.user.email }, { status: 201 })
    }

    // ── REMOVE USER ───────────────────────────────────────────────────
    if (action === 'remove-user' && method === 'DELETE') {
      const body   = await req.json().catch(() => null) as { userId?: string } | null
      const userId = body?.userId

      if (!userId) return Response.json({ error: 'userId is required' }, { status: 400 })

      const { error } = await ctx.supabaseAdmin.auth.admin.deleteUser(userId)
      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ deleted: userId })
    }

    return Response.json({ error: 'Unknown action or method' }, { status: 400 })
  }),
)
