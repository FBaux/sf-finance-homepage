# GBR Portal — Supabase Setup

## 1. Supabase Projekt erstellen

1. Gehe zu **https://supabase.com** → „Start your project" → mit GitHub anmelden
2. Klick auf **„New project"**
3. Name: `daydom-gbr-portal` (oder beliebig)
4. Datenbank-Passwort: sicher wählen und speichern
5. Region: **Frankfurt (eu-central-1)**
6. Auf **„Create new project"** klicken — dauert ~1 Minute

---

## 2. API-Zugangsdaten kopieren

1. Im Projekt: **Settings → API**
2. Kopiere:
   - **Project URL** → `https://xxxx.supabase.co`
   - **anon public key** → langer JWT-Token
3. Öffne `portal.html` und ersetze Zeile 4–5 im `<script>`-Block:

```js
const SUPABASE_URL      = 'https://DEIN-PROJEKT.supabase.co';
const SUPABASE_ANON_KEY = 'DEIN-ANON-KEY';
```

---

## 3. Storage-Bucket anlegen

1. Im Supabase-Projekt: **Storage → New bucket**
2. Name: `portal-files`
3. **Private** lassen (kein Public-Häkchen)
4. Auf **„Save"** klicken

---

## 4. Storage-Richtlinien setzen (SQL Editor)

1. Im Projekt: **SQL Editor → New query**
2. Folgenden Code einfügen und auf **„Run"** klicken:

```sql
-- Dateien hochladen (alle eingeloggten Nutzer)
CREATE POLICY "Authenticated upload"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'portal-files');

-- Dateien anzeigen / herunterladen
CREATE POLICY "Authenticated select"
ON storage.objects FOR SELECT TO authenticated
USING (bucket_id = 'portal-files');

-- Dateien löschen
CREATE POLICY "Authenticated delete"
ON storage.objects FOR DELETE TO authenticated
USING (bucket_id = 'portal-files');

-- Dateien aktualisieren (upsert)
CREATE POLICY "Authenticated update"
ON storage.objects FOR UPDATE TO authenticated
USING (bucket_id = 'portal-files');
```

---

## 5. Die 4 Nutzer anlegen

1. Im Projekt: **Authentication → Users → Add user → Create new user**
2. Für jeden der 4 GBR-Partner:
   - E-Mail-Adresse eingeben
   - Sicheres Passwort setzen
   - Häkchen bei **„Auto confirm user"** setzen
   - **„Create user"** klicken

> Tipp: E-Mail-Adressen und Passwörter sicher an die Mitglieder weitergeben
> (z. B. per verschlüsselter Nachricht).

---

## 6. Fertig!

Das Portal ist unter `/portal.html` erreichbar.

Optional: Link in der Hauptnavigation hinzufügen (in `index.html` im Nav-Bereich).

---

## Dateitypen & Ordner

Im Portal können alle gängigen Dateitypen gespeichert werden:
- **Verträge**: PDF, DOCX
- **Belege**: PDF, JPG, PNG
- **Social Media**: Screenshots (PNG/JPG), Videos (MP4)
- **Trading**: Screenshots, XLSX, CSV, PDF

Maximale Dateigröße: 50 MB pro Datei (Supabase Free-Tier Standard).
