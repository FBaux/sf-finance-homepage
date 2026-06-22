/**
 * Portal Admin API
 *
 * Privileged operations that require the service-role key (RLS bypassed).
 * Only callable with auth: "secret" — the secret key is never exposed
 * to the browser.
 *
 * Routes (via ?action=<name>):
 *   list-users   — list all portal members
 *   invite-user  — create a new Supabase Auth user
 *   remove-user  — delete a user from Auth
 *
 * ⚠️  Never expose this handler publicly.  Restrict it to internal calls
 *    or protect it with an additional secret header check.
 */

import { withSupabase } from '@supabase/server'

export default {
  fetch: withSupabase({ auth: 'secret', cors: false }, async (req, ctx) => {
    const url    = new URL(req.url)
    const action = url.searchParams.get('action') ?? ''
    const method = req.method.toUpperCase()

    // ── LIST all portal users ────────────────────────────────────────────
    if (action === 'list-users' && method === 'GET') {
      const { data, error } = await ctx.supabaseAdmin.auth.admin.listUsers()
      if (error) return Response.json({ error: error.message }, { status: 500 })

      const users = data.users.map(u => ({
        id:         u.id,
        email:      u.email,
        created_at: u.created_at,
        last_sign_in_at: u.last_sign_in_at,
      }))
      return Response.json({ users })
    }

    // ── INVITE a new user ────────────────────────────────────────────────
    if (action === 'invite-user' && method === 'POST') {
      const body = await req.json().catch(() => null)
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

    // ── REMOVE a user ────────────────────────────────────────────────────
    if (action === 'remove-user' && method === 'DELETE') {
      const body   = await req.json().catch(() => null)
      const userId = body?.userId

      if (!userId) return Response.json({ error: 'userId is required' }, { status: 400 })

      const { error } = await ctx.supabaseAdmin.auth.admin.deleteUser(userId)
      if (error) return Response.json({ error: error.message }, { status: 500 })
      return Response.json({ deleted: userId })
    }

    return Response.json({ error: 'Unknown action or method' }, { status: 400 })
  }),
}
