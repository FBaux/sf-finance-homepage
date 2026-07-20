import React from "react";

/* ============ Reveal (progressive enhancement — content is ALWAYS visible without JS) ============ */
export function Reveal({ children, className = "", delay = 0, as: Tag = "div" }) {
  const ref = React.useRef(null);
  const [inView, setInView] = React.useState(false);
  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          io.disconnect();
        }
      },
      { threshold: 0.15 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <Tag
      ref={ref}
      className={`reveal ${inView ? "in-view" : ""} ${className}`}
      style={delay ? { animationDelay: delay + "ms" } : undefined}
    >
      {children}
    </Tag>
  );
}

/* ============ Design-system primitives ============ */
export function Button({ href, onClick, variant = "solid", className = "", children, type }) {
  const cls = `btn ${variant === "outline" ? "btn-outline" : "btn-solid"} ${className}`;
  if (href) {
    return (
      <a href={href} className={cls}>
        {children}
      </a>
    );
  }
  return (
    <button type={type || "button"} onClick={onClick} className={cls}>
      {children}
    </button>
  );
}

export function SectionHeading({ eyebrow, title, accent, id, align }) {
  const HeadingId = id ? id + "-heading" : undefined;
  return (
    <div style={{ textAlign: align === "center" ? "center" : "left" }}>
      <p className="eyebrow" style={{ marginBottom: 14 }}>{eyebrow}</p>
      <h2 id={HeadingId} style={{ fontSize: "var(--text-h2)", lineHeight: 1.1 }}>
        {title} {accent ? <em style={{ color: "var(--gold-0)", fontStyle: "italic" }}>{accent}</em> : null}
      </h2>
    </div>
  );
}

export function Card({ index, title, children, href, linkLabel }) {
  return (
    <article className="card">
      <span className="card-index" aria-hidden="true">{index}</span>
      <h3 className="card-title">{title}</h3>
      <p className="card-body">{children}</p>
      {href && (
        <a href={href} className="card-link">
          {linkLabel || "Mehr erfahren"} →
        </a>
      )}
    </article>
  );
}

export function MetricTile({ value, label, pending }) {
  return (
    <div className="metric-tile">
      <span className={`metric-value ${pending ? "pending" : ""}`}>{value}</span>
      <span className="metric-label">{label}</span>
    </div>
  );
}

/* ============ Navigation ============ */
const NAV_LINKS = [
  { label: "Trading", href: "#geschaeftsbereiche" },
  { label: "Performance", href: "#performance" },
  { label: "Prop-Firm-Vergleich", href: "vergleich.html" },
  { label: "Über uns", href: "#ueber-uns" },
  { label: "Kontakt", href: "#kontakt" },
];

export function Nav() {
  const [scrolled, setScrolled] = React.useState(false);
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  React.useEffect(() => {
    if (!open) return;
    const onKey = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <nav className={`site-nav ${scrolled ? "scrolled" : ""}`} aria-label="Hauptnavigation">
        <div className="site-nav-inner">
          <a href="#top" className="wordmark">
            DAY<span>DOM</span>
          </a>
          <ul className="nav-links">
            {NAV_LINKS.map((l) => (
              <li key={l.label}>
                <a href={l.href}>{l.label}</a>
              </li>
            ))}
          </ul>
          <div className="nav-right">
            <Button href="mitglieder/" variant="solid" className="nav-cta">
              Mitgliederbereich
            </Button>
            <button
              className="hamburger"
              aria-label="Menü öffnen"
              aria-expanded={open}
              aria-controls="mobile-menu"
              onClick={() => setOpen(true)}
            >
              <span></span><span></span><span></span>
            </button>
          </div>
        </div>
      </nav>
      <div id="mobile-menu" className={`mobile-menu ${open ? "open" : ""}`} role="dialog" aria-modal="true" aria-label="Menü" hidden={!open}>
        <div className="mobile-menu-head">
          <button className="mobile-menu-close" aria-label="Menü schließen" onClick={() => setOpen(false)}>
            ✕
          </button>
        </div>
        <ul className="mobile-menu-links">
          {NAV_LINKS.map((l) => (
            <li key={l.label}>
              <a href={l.href} onClick={() => setOpen(false)}>{l.label}</a>
            </li>
          ))}
        </ul>
        <div className="mobile-menu-cta">
          <Button href="mitglieder/" variant="solid" className="btn-block">
            Mitgliederbereich
          </Button>
        </div>
      </div>
    </>
  );
}

/* ============ Hero ============ */
function usePrefersReducedMotion() {
  const [reduced, setReduced] = React.useState(false);
  React.useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return reduced;
}

function HeroParticles({ count = 18 }) {
  const dots = React.useMemo(
    () =>
      [...Array(count)].map((_, i) => {
        const r = (n) => {
          const x = Math.sin(i * 127.1 + n * 311.7) * 43758.5453;
          return x - Math.floor(x);
        };
        return { left: r(1) * 100, top: 20 + r(2) * 75, size: 2 + r(3) * 3, dur: 9 + r(4) * 14, delay: -r(5) * 20 };
      }),
    [count]
  );
  return (
    <div className="hero-particles" aria-hidden="true">
      {dots.map((d, i) => (
        <span
          key={i}
          style={{
            left: d.left + "%",
            top: d.top + "%",
            width: d.size,
            height: d.size,
            animationDuration: d.dur + "s",
            animationDelay: d.delay + "s",
          }}
        />
      ))}
    </div>
  );
}

const HERO_WORDS = ["Transparent", "Ehrlich", "Nachvollziehbar"];

export function Hero() {
  const reducedMotion = usePrefersReducedMotion();
  const [wordIndex, setWordIndex] = React.useState(0);
  React.useEffect(() => {
    if (reducedMotion) return;
    const iv = setInterval(() => setWordIndex((w) => (w + 1) % HERO_WORDS.length), 2600);
    return () => clearInterval(iv);
  }, [reducedMotion]);

  return (
    <header className="hero" id="top">
      <div className="hero-bg" style={{ backgroundImage: "url(assets/img/hero-tower.png)" }} role="img" aria-label="Architektur bei Nacht, Düsseldorf"></div>
      <div className="hero-scrim" aria-hidden="true"></div>
      {!reducedMotion && <HeroParticles />}
      <div className="hero-inner">
        <p className="eyebrow">Prop Trading · Transparenz · Education</p>
        <h1>
          Prop Trading.<br />
          <span className="hero-rotate" aria-live="off">
            {HERO_WORDS.map((w, i) => (
              <em key={w} style={{ opacity: i === wordIndex ? 1 : 0 }} aria-hidden={i !== wordIndex}>
                {w}
              </em>
            ))}
            <span className="visually-hidden">{HERO_WORDS[wordIndex]}</span>
          </span>{" "}
          dokumentiert.
        </h1>
        <p className="hero-sub">
          Echte Accounts, klare Regeln und nachvollziehbare Ergebnisse – ohne Gewinnversprechen und ohne Guru-Inszenierung.
        </p>
        <div className="hero-ctas">
          <Button href="#performance" variant="solid">Performance ansehen</Button>
          <Button href="vergleich.html" variant="outline">Prop Firms vergleichen</Button>
        </div>
      </div>
    </header>
  );
}

/* ============ Trust bar ============ */
export function TrustBar() {
  const items = ["Düsseldorf", "Gegründet 2026", "Regelbasiertes Trading", "Transparente Affiliate-Kennzeichnung"];
  return (
    <div className="trust-bar">
      <div className="trust-bar-inner">
        {items.map((t, i) => (
          <span key={t}>
            {i > 0 && <span aria-hidden="true">· </span>}
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ============ Positioning ============ */
export function Positioning() {
  return (
    <section id="ueber-uns" className="section" style={{ background: "var(--ink-1)" }} aria-labelledby="ueber-uns-heading">
      <div className="container grid-2">
        <Reveal>
          <SectionHeading id="ueber-uns" eyebrow="Über uns" title="Struktur statt" accent="Inszenierung." />
          <p style={{ marginTop: 26, maxWidth: 480 }}>
            DayDom dokumentiert den Aufbau regelbasierter Prop-Trading-Systeme – einschließlich Setups, Risikomanagement, Drawdowns und Fehlern. Affiliate-Empfehlungen und Bildungsangebote werden transparent gekennzeichnet.
          </p>
        </Reveal>
        <Reveal delay={120}>
          <img src="assets/img/about-aerial.png" alt="Architekturaufnahme bei Nacht, Symbolbild für Struktur und Präzision" loading="lazy" style={{ width: "100%", aspectRatio: "4/3", objectFit: "cover" }} />
        </Reveal>
      </div>
    </section>
  );
}

/* ============ Transparency / Performance ============ */
export function Transparency() {
  return (
    <section id="performance" className="section" aria-labelledby="performance-heading">
      <div className="container">
        <Reveal>
          <SectionHeading id="performance" eyebrow="Performance & Transparenz" title="Ergebnisse." accent="Nachvollziehbar." align="center" />
        </Reveal>
        <Reveal delay={100}>
          <div className="metric-grid" style={{ marginTop: 48 }}>
            <MetricTile value="2" label="Aktive Funded Accounts" />
            <MetricTile value="Noch nicht veröffentlicht" pending label="Kumulierte Payouts" />
            <MetricTile value="Noch nicht veröffentlicht" pending label="Maximaler Drawdown" />
            <MetricTile value="Verifizierung folgt" pending label="Dokumentierter Zeitraum" />
            <MetricTile value="Verifizierung folgt" pending label="Bestandene / Verlorene Challenges" />
            <MetricTile value="Verifizierung folgt" pending label="Letzte Aktualisierung" />
          </div>
        </Reveal>
        <p className="metric-note">
          $150k nominales Funded-Account-Volumen (Lucid $100k · IQ Capital $50k). Funded-Account-Größen entsprechen nicht dem verfügbaren Risikokapital, Eigenkapital oder erzielten Gewinn.
        </p>
        <Reveal delay={200}>
          <div style={{ marginTop: 30 }}>
            <Button href="dashboard.html" variant="outline">Transparenz-Dashboard öffnen</Button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ============ Pillars / Geschäftsbereiche ============ */
export function Pillars() {
  return (
    <section id="geschaeftsbereiche" className="section" style={{ background: "var(--ink-1)" }} aria-labelledby="geschaeftsbereiche-heading">
      <div className="container">
        <Reveal>
          <SectionHeading id="geschaeftsbereiche" eyebrow="Geschäftsbereiche" title="Drei Säulen." accent="Eine Struktur." align="center" />
        </Reveal>
        <div className="card-grid" style={{ marginTop: 48 }}>
          <Reveal><Card index="01" title="Prop Trading" href="#performance" linkLabel="Performance ansehen">
            Regelbasierte Strategien, fest definierte Risikolimits und transparente Dokumentation unserer Funded Accounts.
          </Card></Reveal>
          <Reveal delay={100}><Card index="02" title="Prop-Firm-Vergleich" href="vergleich.html" linkLabel="Vergleich öffnen">
            Nachvollziehbare Vergleiche von Regeln, Kosten und Auszahlungsbedingungen. Affiliate-Partnerschaften werden klar gekennzeichnet.
          </Card></Reveal>
          <Reveal delay={200}><Card index="03" title="Education" href="mitglieder/" linkLabel="Zum Kursbereich">
            Praxisnahe Inhalte zu Setups, Risikomanagement und Trading-Psychologie. Keine Gewinnversprechen.
          </Card></Reveal>
        </div>
      </div>
    </section>
  );
}

/* ============ Content preview ============ */
export function ContentPreview() {
  const tiles = [
    { img: "content-1.png", t: "Prop Trading erklärt", s: "Was ist ein Funded Account?" },
    { img: "content-2.png", t: "Erste Erfahrungen mit Payouts", s: "Ablauf und Auszahlungsbedingungen" },
    { img: "content-3.png", t: "Chart-Analyse", s: "Setup-Aufbau Schritt für Schritt" },
  ];
  return (
    <section id="content" className="section" aria-labelledby="content-heading">
      <div className="container">
        <Reveal>
          <SectionHeading id="content" eyebrow="Social Media" title="Content." accent="In Vorbereitung." align="center" />
        </Reveal>
        <div className="card-grid" style={{ marginTop: 48 }}>
          {tiles.map((x, i) => (
            <Reveal key={x.t} delay={i * 100}>
              <div className="content-card">
                <img src={"assets/img/" + x.img} alt="" loading="lazy" />
                <div className="content-card-body">
                  <span className="badge">Geplant</span>
                  <h3 style={{ fontFamily: "var(--font-display)", fontSize: 19, color: "var(--cream-0)" }}>{x.t}</h3>
                  <p style={{ fontSize: 13.5, color: "var(--cream-2)", margin: "6px 0 0" }}>{x.s}</p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
        <div style={{ textAlign: "center", marginTop: 40 }}>
          <Button href="mitglieder/" variant="outline">Alle Inhalte ansehen</Button>
        </div>
      </div>
    </section>
  );
}

/* ============ Credibility (replaces fabricated testimonials) ============ */
export function Credibility() {
  return (
    <section className="section" style={{ background: "var(--ink-1)" }} aria-labelledby="credibility-heading">
      <div className="container" style={{ maxWidth: 720, textAlign: "center" }}>
        <Reveal>
          <h2 id="credibility-heading" style={{ fontSize: "var(--text-h2)" }}>Transparenz muss belegbar sein.</h2>
          <p style={{ marginTop: 20 }}>
            Kundenstimmen, Payouts und Performance-Angaben veröffentlichen wir nur, wenn sie nachvollziehbar dokumentiert und zur Veröffentlichung freigegeben sind.
          </p>
        </Reveal>
      </div>
    </section>
  );
}

/* ============ Team ============ */
const FOUNDERS = [
  { ini: "FD", name: "Fabian Diefke", role: "Co-Founder · Geschäftsführung", bio: "Verantwortlich für Strategie, Prop Trading und technische Umsetzung.", tags: ["Prop Trading", "Strategie", "Tech"] },
  { ini: "SS", name: "Shinthugan Sivasunthararajan", role: "Co-Founder · Geschäftsführung", bio: "Verantwortlich für Affiliate Marketing, Social Media und Education.", tags: ["Affiliate", "Social Media", "Education"] },
  { ini: "AB", name: "Abdelillah Benouahi", role: "Co-Founder · Geschäftsführung", bio: "Verantwortlich für Content-Produktion und Prop Trading.", tags: ["Prop Trading", "Content"] },
];

export function Team() {
  return (
    <section id="team" className="section" aria-labelledby="team-heading">
      <div className="container">
        <Reveal>
          <SectionHeading id="team" eyebrow="Gründer" title="Die" accent="Menschen." />
          <p style={{ marginTop: 12, marginBottom: 40, maxWidth: 520 }}>hinter DayDom Performance Group. Drei Gründer, eine GbR.</p>
        </Reveal>
        <div className="team-grid">
          {FOUNDERS.map((f, i) => (
            <Reveal key={f.ini} delay={i * 100}>
              <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                <div className="team-photo" aria-hidden="true">Foto folgt — {f.name}</div>
                <div style={{ padding: "24px 26px" }}>
                  <h3 className="card-title" style={{ fontSize: 21 }}>{f.name}</h3>
                  <p className="eyebrow" style={{ margin: "6px 0 14px" }}>{f.role}</p>
                  <p className="card-body">{f.bio}</p>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 16 }}>
                    {f.tags.map((t) => (
                      <span key={t} className="tag">{t}</span>
                    ))}
                  </div>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ============ Contact ============ */
export function Contact() {
  return (
    <section id="kontakt" className="section" style={{ background: "var(--ink-1)" }} aria-labelledby="kontakt-heading">
      <div className="container grid-2">
        <Reveal>
          <SectionHeading id="kontakt" eyebrow="Kontakt" title="Fragen zu" accent="DayDom?" />
          <p style={{ marginTop: 18, maxWidth: 460 }}>Schreib uns zu Kooperationen, Inhalten oder unseren Angeboten.</p>
          <p style={{ marginTop: 10, fontSize: 13.5, color: "var(--cream-2)" }}>
            Ein Kontaktformular folgt in Kürze. Bis dahin erreichst du uns direkt per E-Mail.
          </p>
          <div style={{ marginTop: 26 }}>
            <Button href="mailto:info@fsfinance.de" variant="solid">info@fsfinance.de</Button>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {[
              ["Standort", "Düsseldorf, Deutschland"],
              ["Unternehmen", "Diefke & Sivasunthararajan GbR"],
              ["Kapital", "$100k Lucid · $50k IQ Capital (nominales Funded-Volumen)"],
            ].map(([k, v]) => (
              <div key={k}>
                <p className="eyebrow" style={{ marginBottom: 4 }}>{k}</p>
                <p style={{ color: "var(--cream-0)", margin: 0 }}>{v}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ============ Footer ============ */
export function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 32 }}>
          <div>
            <div className="wordmark" style={{ fontSize: 18 }}>DAY<span>DOM</span></div>
            <p className="eyebrow" style={{ marginTop: 10 }}>Performance Group · Est. 2026</p>
          </div>
          <ul className="footer-links">
            <li><a href="impressum.html">Impressum</a></li>
            <li><a href="datenschutz.html">Datenschutz</a></li>
            <li><a href="#risikohinweis">Risikohinweis</a></li>
            <li><a href="#risikohinweis">Affiliate-Hinweis</a></li>
            <li><a href="vergleich.html">Prop-Firm-Vergleich</a></li>
            <li><a href="mitglieder/">Mitgliederbereich</a></li>
          </ul>
        </div>
        <ul className="social-list" style={{ marginTop: 28 }} aria-label="Social-Media-Kanäle (folgen)">
          <li>Instagram <span className="visually-hidden">— folgt</span> <span aria-hidden="true">(folgt)</span></li>
          <li>TikTok <span aria-hidden="true">(folgt)</span></li>
          <li>YouTube <span aria-hidden="true">(folgt)</span></li>
        </ul>
        <div id="risikohinweis" className="risk-notice">
          <strong style={{ color: "var(--cream-0)" }}>Risikohinweis:</strong> Der Handel mit Futures, Devisen und anderen gehebelten Finanzinstrumenten ist mit erheblichen Risiken verbunden und kann zum vollständigen Verlust des eingesetzten Kapitals führen. Vergangene Ergebnisse sind kein Indikator für zukünftige Entwicklungen. Die Inhalte auf dieser Seite dienen ausschließlich Informations- und Bildungszwecken und stellen keine Anlageberatung dar.
          <br /><br />
          <strong style={{ color: "var(--cream-0)" }}>Affiliate-Hinweis:</strong> Links zu Prop Firms und Tools können Affiliate-Links sein und werden entsprechend gekennzeichnet.
          <br /><br />
          Funded-Account-Größen sind kein Nachweis für Gewinne oder verwaltetes Kundenvermögen.
        </div>
        <p style={{ fontSize: 12, color: "var(--cream-2)", marginTop: 24 }}>© 2026 Diefke & Sivasunthararajan GbR</p>
      </div>
    </footer>
  );
}
