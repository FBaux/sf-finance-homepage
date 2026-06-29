// ═══════════════════════════════════════════════════════════
//  DayDom Performance Group — Supabase Auth Module
//  Konfiguration: SUPABASE_URL und SUPABASE_ANON_KEY unten anpassen
// ═══════════════════════════════════════════════════════════

const SUPABASE_URL  = 'https://gymhfbnljbosqxqqzdik.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_XCtT7o-kMVYfvoehu26P2Q_esQAvVIY';

let _supabase = null;

function getSupabase() {
  if (!_supabase) {
    _supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  }
  return _supabase;
}

async function getUser() {
  const { data: { user } } = await getSupabase().auth.getUser();
  return user;
}

async function getSession() {
  const { data: { session } } = await getSupabase().auth.getSession();
  return session;
}

async function signUp(email, password) {
  const { data, error } = await getSupabase().auth.signUp({ email, password });
  return { data, error };
}

async function signIn(email, password) {
  const { data, error } = await getSupabase().auth.signInWithPassword({ email, password });
  return { data, error };
}

async function signOut() {
  const { error } = await getSupabase().auth.signOut();
  if (!error) {
    window.location.href = '/mitglieder/login.html';
  }
  return { error };
}

async function requireAuth() {
  const session = await getSession();
  if (!session) {
    window.location.href = '/mitglieder/login.html';
    return null;
  }
  return session;
}

async function redirectIfLoggedIn() {
  const session = await getSession();
  if (session) {
    window.location.href = '/mitglieder/';
    return true;
  }
  return false;
}
