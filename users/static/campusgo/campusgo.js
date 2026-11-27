/*
  CampusGo — perilaku kecil sisi browser (tanpa framework).
  1. Navbar responsif: satu <nav>, popover saat tidak muat, sebaris saat muat.
  2. Menu akun: sinkron aria-expanded + posisi cadangan tanpa anchor positioning.
  3. Tombol "Lihat" password.
  4. Validasi form: sinkron aria-invalid dengan :user-invalid + umumkan error.
  5. Cegah kirim dua kali setelah form valid dikirim.
*/
(() => {
  const isOpen = (el) => el.matches(":is(:popover-open, .\\:popover-open)");

  /* ---------- 1. Navbar responsif ---------- */
  const header = document.querySelector(".site-header");
  const inner = header?.querySelector(".header-inner");
  const siteMenu = header?.querySelector("#site-menu");

  if (header && inner && siteMenu && "ResizeObserver" in window) {
    let lastWidth = 0;
    const updateLayout = () => {
      const width = inner.clientWidth;
      const wasWide = header.classList.contains("is-wide");
      // Saat menu terlipat, ukur ulang hanya kalau header bertambah lebar (hindari layout thrash).
      if (!wasWide && width <= lastWidth) return;
      lastWidth = width;

      const wasOpen = siteMenu.hasAttribute("popover") && isOpen(siteMenu);
      header.classList.add("is-measuring", "is-wide");
      const wide = inner.scrollWidth <= inner.clientWidth;
      header.classList.toggle("is-wide", wide);

      if (wide) {
        siteMenu.removeAttribute("popover");
      } else if (!siteMenu.hasAttribute("popover")) {
        siteMenu.setAttribute("popover", "auto");
        if (wasOpen) siteMenu.showPopover();
      }
      requestAnimationFrame(() => header.classList.remove("is-measuring"));
    };
    const ro = new ResizeObserver(updateLayout);
    ro.observe(header);
    ro.observe(siteMenu);
  }

  /* ---------- 2. Menu akun ---------- */
  const accountMenu = document.getElementById("account-menu");
  const accountButton = document.querySelector('[popovertarget="account-menu"]');
  if (accountMenu && accountButton) {
    accountMenu.addEventListener("toggle", (event) => {
      const open = event.newState === "open";
      accountButton.setAttribute("aria-expanded", String(open));
      // Browser tanpa CSS anchor positioning: hitung posisi manual di bawah tombol.
      if (open && !CSS.supports("position-area", "block-end")) {
        const t = accountButton.getBoundingClientRect();
        const size = accountMenu.getBoundingClientRect();
        let top = t.bottom + 8;
        if (top + size.height > innerHeight) top = Math.max(0, t.top - size.height - 8);
        const left = Math.min(Math.max(0, t.right - size.width), innerWidth - size.width);
        accountMenu.style.top = `${top}px`;
        accountMenu.style.left = `${left}px`;
      }
    });
  }

  /* ---------- 3. Tombol lihat password ---------- */
  document.querySelectorAll("[data-password-toggle]").forEach((button) => {
    const input = document.getElementById(button.dataset.passwordToggle);
    if (!input) return;
    button.addEventListener("click", () => {
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-pressed", String(show));
      button.setAttribute("aria-label", show ? "Sembunyikan password" : "Tampilkan password");
      button.textContent = show ? "Tutup" : "Lihat";
    });
  });

  /* ---------- 4. Validasi: aria-invalid mengikuti :user-invalid ---------- */
  const fieldSelector = "input, select, textarea";

  const linkError = (el, shown) => {
    const errorId = el.dataset.error;
    if (!errorId) return;
    const ids = (el.getAttribute("aria-describedby") || "")
      .split(/\s+/)
      .filter((id) => id && id !== errorId);
    if (shown) ids.push(errorId);
    if (ids.length) el.setAttribute("aria-describedby", ids.join(" "));
    else el.removeAttribute("aria-describedby");
  };

  // Satu live region sopan untuk seluruh halaman.
  const announcer = document.createElement("div");
  announcer.setAttribute("aria-live", "polite");
  announcer.className = "sr-only";
  document.body.append(announcer);
  let announceTimer;
  let announcedField;

  const announceError = (el) => {
    const error = document.getElementById(el.dataset.error);
    if (!error || !error.textContent.trim()) return;
    const label = el.labels?.[0] ? `${el.labels[0].textContent.replace(/[*\s]+/g, " ").trim()}: ` : "";
    clearTimeout(announceTimer);
    announcer.textContent = "";
    announcedField = el;
    // Tunggu pembaca layar selesai menyebut field berikutnya.
    announceTimer = setTimeout(() => { announcer.textContent = label + error.textContent.trim(); }, 500);
  };

  const flagged = new WeakSet();
  const announced = new WeakSet();

  const syncAria = (el, announce = false) => {
    if (!el.matches?.(fieldSelector) || !el.dataset.error) return;
    const invalid = el.matches(":user-invalid");
    const error = document.getElementById(el.dataset.error);
    if (invalid) {
      if (error) error.textContent = el.validationMessage; // pesan bawaan browser (sesuai bahasa)
      if (announce && !announced.has(el)) {
        announceError(el);
        announced.add(el);
      }
      el.setAttribute("aria-invalid", "true");
      linkError(el, true);
      flagged.add(el);
    } else if (flagged.has(el)) {
      el.setAttribute("aria-invalid", "false");
      linkError(el, false);
      if (error) error.textContent = "";
      flagged.delete(el);
      announced.delete(el);
      if (announcedField === el) {
        clearTimeout(announceTimer);
        announcer.textContent = "";
      }
    }
  };

  document.addEventListener("blur", (e) => syncAria(e.target, true), true);
  document.addEventListener("change", (e) => syncAria(e.target, true), true);
  document.addEventListener("input", (e) => {
    // Error dari server (aria-invalid="true" awal) dibersihkan begitu pengguna mengetik ulang.
    if (e.target.matches?.(fieldSelector) && e.target.getAttribute("aria-invalid") === "true" && !flagged.has(e.target)) {
      e.target.setAttribute("aria-invalid", "false");
    }
    syncAria(e.target);
  });
  // Submit gagal: browser memicu 'invalid' di tiap field & memindahkan fokus ke field pertama.
  document.addEventListener("invalid", (e) => {
    announced.add(e.target);
    syncAria(e.target);
  }, true);

  // Error dari server: arahkan fokus ke field pertama yang ditolak.
  document.querySelector('main [aria-invalid="true"]')?.focus();

  /* ---------- 5. Cegah double submit ---------- */
  document.addEventListener("submit", (e) => {
    const form = e.target;
    if (e.defaultPrevented || form.method.toLowerCase() !== "post") return;
    const submitter = e.submitter;
    if (!submitter) return;
    // Dinonaktifkan setelah event selesai supaya nilai tombol tetap ikut terkirim.
    setTimeout(() => { submitter.disabled = true; }, 0);
  });
})();
