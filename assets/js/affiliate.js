/* Affiliate-Links aus assets/affiliate.json auf die CTAs von vergleich.html verdrahten.
   Gepflegt wird ausschliesslich die JSON-Datei — dieses Skript wird nicht angefasst.

   Zustaende pro Button:
   - URL hinterlegt  -> echter Link, rel="sponsored nofollow noopener", oeffnet neuen Tab
   - URL leer        -> sichtbar deaktiviert statt totem #-Link (Nutzer klickt nicht ins Leere)  */

(function () {
  "use strict";

  var targets = document.querySelectorAll("a[data-affiliate]");
  if (!targets.length) return;

  function disable(el) {
    el.removeAttribute("href");
    el.setAttribute("aria-disabled", "true");
    el.classList.add("btn-pending");
    el.title = "Partnerprogramm noch nicht freigeschaltet";
  }

  function activate(el, url) {
    el.href = url;
    el.rel = "sponsored nofollow noopener";
    el.target = "_blank";
  }

  fetch("assets/affiliate.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (cfg) {
      var links = (cfg && cfg.links) || {};
      targets.forEach(function (el) {
        var url = links[el.dataset.affiliate];
        if (typeof url === "string" && url.trim()) activate(el, url.trim());
        else disable(el);
      });
    })
    .catch(function () {
      // Config nicht ladbar: lieber deaktiviert als toter Link.
      targets.forEach(disable);
    });
})();
