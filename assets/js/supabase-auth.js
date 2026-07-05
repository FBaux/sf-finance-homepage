// ═══════════════════════════════════════════════════════════
//  DayDom Performance Group — Supabase Auth Module
//  Konfiguration: SUPABASE_URL und SUPABASE_ANON_KEY unten anpassen
// ═══════════════════════════════════════════════════════════

const SUPABASE_URL  = 'https://gymhfbnljbosqxqqzdik.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5bWhmYm5samJvc3F4cXF6ZGlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxMzE3NDMsImV4cCI6MjA5NzcwNzc0M30.u2mvAnEe7QvOSgcv-U7X7qgrIQ7Mc9_EviXPctEAZoM';

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

async function requireAdmin() {
  const session = await requireAuth();
  if (!session) return null;
  const user = session.user;
  const role = (user.app_metadata && user.app_metadata.role) || '';
  if (role !== 'admin') {
    window.location.href = '/mitglieder/';
    return null;
  }
  return session;
}

// Lädt geschützten HTML-Inhalt aus dem privaten Storage-Bucket "kurs".
// Wirft bei Fehler (z. B. 401/403 wenn die Session serverseitig ungültig ist).
async function fetchProtected(objectPath) {
  const { data, error } = await getSupabase().storage.from('kurs').download(objectPath);
  if (error) throw error;
  return await data.text();
}

async function redirectIfLoggedIn() {
  const session = await getSession();
  if (session) {
    window.location.href = '/mitglieder/';
    return true;
  }
  return false;
}
