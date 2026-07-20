import React from "react";
import { createRoot } from "react-dom/client";
import {
  Nav, Hero, TrustBar, Positioning, Transparency, Pillars,
  ContentPreview, Credibility, Team, Contact, Footer,
} from "./components.jsx";

function App() {
  return (
    <>
      <Nav />
      <main id="main-content">
        <Hero />
        <TrustBar />
        <Positioning />
        <Transparency />
        <Pillars />
        <ContentPreview />
        <Credibility />
        <Team />
        <Contact />
      </main>
      <Footer />
    </>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
