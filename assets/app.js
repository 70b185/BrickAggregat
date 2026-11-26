/* Brick Aggregat website: reads export/*.json and renders five tabs. No build step, no dependencies. */
(function () {
  "use strict";
  const REPO = "https://github.com/70b185/BrickAggregat";
  const $ = (s, el) => (el || document).querySelector(s);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const view = $("#view");
  let DATA = null, NEWS = [], DISC = [];
  const params = new URLSearchParams(location.search);
  const state = {
    t: params.get("t") || "projects", c: params.get("c") || "all", q: params.get("q") || "",
    fw: params.get("fw") || "", d: params.get("d") || "", sort: params.get("sort") || "activity",
    foss: params.get("foss") === "1", old: params.get("old") === "1",
  };

  function saveUrl() {
    const p = new URLSearchParams();
    if (state.t !== "projects") p.set("t", state.t);
    if (state.t === "projects") {
      if (state.c !== "all") p.set("c", state.c);
      if (state.q) p.set("q", state.q);
      if (state.fw) p.set("fw", state.fw);
      if (state.d) p.set("d", state.d);
      if (state.sort !== "activity") p.set("sort", state.sort);
      if (state.foss) p.set("foss", "1");
      if (state.old) p.set("old", "1");
    }
    const s = p.toString();
    history.replaceState(null, "", s ? "?" + s : location.pathname);
  }

  function load(path, fallback) {
    return fetch(path, { cache: "no-cache" }).then(r => (r.ok ? r.json() : fallback)).catch(() => fallback);
  }

  const catLabel = id => (DATA.categories.find(c => c.id === id) || { label: id }).label;
  const fwLabel = id => DATA.firmwares[id] || id;
  const devLabel = id => DATA.devices[id] || id;
  const ACT = { active: "commits in the last 90 days", quiet: "last commit 3-12 months ago", dormant: "no commit for over a year", archived: "archived by its author" };

  function card(p) {
    const flags = [];
    if (p.new) flags.push('<span class="flag new">new</span>');
    if (p.pak_store) flags.push(`<span class="flag" title="Listed in the NextUI Pak Store${p.pak_store.experimental ? " (experimental)" : ""}">Pak Store</span>`);
    if (!p.license && p.repo) flags.push('<span class="flag warn" title="No licence file found in the repo: not free software in the legal sense until the author adds one">no licence</span>');
    if (!p.repo) flags.push('<span class="flag warn" title="No public source repository: download page or website only">no repo</span>');
    else if (p.source === "none" && !["guide", "theme"].includes(p.category)) flags.push('<span class="flag warn" title="The repo holds releases or docs only, no source code">no source</span>');
    if (p.archived) flags.push('<span class="flag warn">archived</span>');
    if (p.unreachable) flags.push(`<span class="flag warn" title="Repo did not answer on ${esc(p.unreachable)}">unreachable</span>`);
    const meta = [];
    if (p.version) meta.push(esc(p.version));
    if (p.license) meta.push(esc(p.license));
    if (p.stars != null) meta.push("★ " + p.stars);
    const tags = p.runs_on.map(f => `<span class="tag" title="runs on">${esc(fwLabel(f))}</span>`)
      .concat(p.devices.map(d => `<span class="tag" title="device">${esc(devLabel(d))}</span>`));
    const text = (p.note || p.description || "") + (p.aliases && p.aliases.length ? ` (also: ${p.aliases.join(", ")})` : "");
    return `<article class="card" style="--cat:var(--c-${esc(p.category)})">
      <div class="top"><span class="dot ${esc(p.activity)}" title="${esc(ACT[p.activity] || "")}"></span>${esc(catLabel(p.category))}
        ${flags.join(" ")}<span class="date" title="last commit">${esc(p.last_commit || "")}</span></div>
      <h3><a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.name)}</a></h3>
      <div class="by">by ${esc(p.author)}${meta.length ? " · " + meta.join(" · ") : ""}</div>
      ${text ? `<p title="${p.note ? "our note" : "the repo's own description"}">${esc(text)}</p>` : ""}
      ${(p.links ? Object.entries(p.links).map(([k, v]) => `<a class="meta" href="${esc(v)}" target="_blank" rel="noopener">${esc(k)}</a>`).join(" · ") : "")}
      <div class="tags">${tags.join("")}</div>
    </article>`;
  }

  function filtered() {
    const q = state.q.trim().toLowerCase();
    let ps = DATA.projects.filter(p =>
      (state.c === "all" || p.category === state.c) &&
      (!state.foss || p.open) &&
      (state.old || p.activity === "active" || p.activity === "quiet") &&
      (!state.fw || p.runs_on.includes(state.fw)) &&
      (!state.d || p.devices.includes(state.d)) &&
      (!q || [p.name, p.author, p.note, p.description, p.url, (p.aliases || []).join(" "), p.runs_on.join(" ")].join(" ").toLowerCase().includes(q)));
    const by = {
      activity: (a, b) => (b.last_commit || "").localeCompare(a.last_commit || ""),
      name: (a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: "base" }),
      stars: (a, b) => (b.stars || 0) - (a.stars || 0),
      added: (a, b) => String(b.added || "").localeCompare(String(a.added || "")) || (b.last_commit || "").localeCompare(a.last_commit || ""),
    }[state.sort];
    return ps.sort(by);
  }

  function countFor(cat) {
    return DATA.projects.filter(p => (cat === "all" || p.category === cat) && (!state.foss || p.open) &&
      (state.old || p.activity === "active" || p.activity === "quiet")).length;
  }

  function renderProjects() {
    const cats = [{ id: "all", label: "All" }].concat(DATA.categories);
    const fwOpts = Object.entries(DATA.firmwares).map(([k, v]) => `<option value="${k}"${state.fw === k ? " selected" : ""}>${esc(v)}</option>`).join("");
    const devOpts = Object.entries(DATA.devices).map(([k, v]) => `<option value="${k}"${state.d === k ? " selected" : ""}>${esc(v)}</option>`).join("");
    const desc = state.c === "all" ? "" : (DATA.categories.find(c => c.id === state.c) || {}).desc || "";
    view.innerHTML = `
      <div class="cats">${cats.map(c => `<button data-c="${c.id}" class="${state.c === c.id ? "on" : ""}">${c.id !== "all" ? `<i style="background:var(--c-${c.id})"></i>` : ""}${esc(c.label)} <span class="n">${countFor(c.id)}</span></button>`).join("")}</div>
      <div class="bar">
        <input type="search" id="q" placeholder="Search name, author, description…" value="${esc(state.q)}">
        <select id="fw"><option value="">Any firmware</option>${fwOpts}</select>
        <select id="d"><option value="">Any device</option>${devOpts}</select>
        <select id="sort">
          <option value="activity"${state.sort === "activity" ? " selected" : ""}>Recently active</option>
          <option value="name"${state.sort === "name" ? " selected" : ""}>Name</option>
          <option value="stars"${state.sort === "stars" ? " selected" : ""}>Stars</option>
          <option value="added"${state.sort === "added" ? " selected" : ""}>Newest in the index</option>
        </select>
        <label title="Only projects with a licence file and source code in a public repo"><input type="checkbox" id="foss"${state.foss ? " checked" : ""}> open source only</label>
        <label title="Also list projects with no commit for over a year, and archived ones"><input type="checkbox" id="old"${state.old ? " checked" : ""}> dormant too</label>
        <span class="count" id="count"></span>
      </div>
      <main>${desc ? `<p class="lead">${esc(desc)}.</p>` : ""}<div class="grid" id="grid"></div></main>`;
    drawGrid();
    view.querySelectorAll(".cats button").forEach(b => b.onclick = () => { state.c = b.dataset.c; saveUrl(); renderProjects(); });
    $("#q").oninput = e => { state.q = e.target.value; saveUrl(); drawGrid(); };
    $("#fw").onchange = e => { state.fw = e.target.value; saveUrl(); drawGrid(); };
    $("#d").onchange = e => { state.d = e.target.value; saveUrl(); drawGrid(); };
    $("#sort").onchange = e => { state.sort = e.target.value; saveUrl(); drawGrid(); };
    $("#foss").onchange = e => { state.foss = e.target.checked; saveUrl(); renderProjects(); };
    $("#old").onchange = e => { state.old = e.target.checked; saveUrl(); renderProjects(); };
  }

  function drawGrid() {
    const ps = filtered();
    $("#grid").innerHTML = ps.length ? ps.map(card).join("") : '<div class="empty">Nothing matches. Try unticking “open source only” or ticking “dormant too”.</div>';
    $("#count").textContent = `${ps.length} shown`;
  }

  function renderNew() {
    const byId = Object.fromEntries(DATA.projects.map(p => [p.id, p]));
    const what = { added: "new in the index", release: "release", "back online": "back online", licence: "licence changed" };
    const ev = NEWS.filter(r => byId[r.id]).slice(0, 80).map(r => {
      const p = byId[r.id];
      return `<div class="row"><span class="d">${esc(r.date)}</span><a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.name)}</a>
        <span class="w">${esc(what[r.what] || r.what)} ${esc(r.detail || "")}</span><span class="tag">${esc(catLabel(p.category))}</span></div>`;
    }).join("");
    const recent = DATA.projects.filter(p => p.open).sort((a, b) => (b.last_commit || "").localeCompare(a.last_commit || "")).slice(0, 40);
    view.innerHTML = `<main>
      <p class="lead">What changed since the index started on 2026-11-24: entries added and releases seen by the three-day check.
        Subscribe with the <a href="feed.xml">Atom feed</a>.</p>
      <h2>Added and released</h2>
      <div class="list">${ev || '<div class="empty">Nothing yet: the first three-day check after the launch fills this list.</div>'}</div>
      <h2>Most recent commits (open-source entries)</h2>
      <div class="list">${recent.map(p => `<div class="row"><span class="d">${esc(p.last_commit)}</span><a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.name)}</a>
        <span class="w">${esc(p.version || "")}</span><span class="tag">${esc(catLabel(p.category))}</span></div>`).join("")}</div>
    </main>`;
  }

  function renderDev() {
    const kb = DATA.kb.filter(k => k.file !== "kb/SOURCES.html");
    const dev = DATA.projects.filter(p => p.category === "dev" && p.open).sort((a, b) => (b.last_commit || "").localeCompare(a.last_commit || "")).slice(0, 12);
    view.innerHTML = `<main>
      <p class="lead">What people building for the Brick family found out, from their public repos: hardware, firmwares,
        toolchains, paks, and sound and MIDI for music apps. Each fact names its source and how sure it is.</p>
      <div class="btns">${kb.map(k => `<a class="btn" href="${esc(k.file)}">${esc(k.title)}<span>${esc(k.md)}</span></a>`).join("")}
        <a class="btn" href="kb/SOURCES.html">Sources<span>every reference used</span></a></div>
      <h2>Developer projects, most recently active</h2>
      <div class="grid">${dev.map(card).join("")}</div>
      <p class="prose" style="margin-top:16px">More in the <a href="?c=dev">Developer list</a>. Something missing or wrong?
        <a href="${REPO}/discussions/new?category=q-a">Ask in Q&amp;A</a> or open a pull request against <code>knowledge/</code>.</p>
    </main>`;
  }

  function renderAsk() {
    const rows = DISC.slice(0, 25).map(d => `<div class="row"><span class="d">${esc(d.updated)}</span>
      <a href="${esc(d.url)}" target="_blank" rel="noopener">${esc(d.title)}</a>
      <span class="w">${esc(d.category || "")} · ${d.comments} repl${d.comments === 1 ? "y" : "ies"}${d.answered ? " · answered" : ""}</span></div>`).join("");
    view.innerHTML = `<main>
      <p class="lead">Questions about developing for the Brick go to GitHub Discussions in this project, where answers stay
        findable. Settled answers move into the knowledge base with their source.</p>
      <div class="btns">
        <a class="btn" href="${REPO}/discussions/new?category=q-a" target="_blank" rel="noopener">Ask a development question<span>Q&amp;A: toolchains, audio, MIDI, input, firmwares</span></a>
        <a class="btn" href="${REPO}/discussions/new?category=show-and-tell" target="_blank" rel="noopener">Show what you built<span>Show and tell: betas, demos, test builds</span></a>
        <a class="btn" href="${REPO}/discussions/new?category=ideas" target="_blank" rel="noopener">Propose an idea<span>Ideas: apps you want, shared libraries, collaborations</span></a>
        <a class="btn" href="${REPO}/discussions" target="_blank" rel="noopener">All discussions<span>browse and search</span></a>
      </div>
      <h2>Recent discussions</h2>
      <div class="list">${rows || '<div class="empty">No discussions yet. Be the first to ask.</div>'}</div>
      <h2>Open questions in the knowledge base</h2>
      <p class="prose">Things sources disagree on, like whether the Brick's bottom USB port can act as a sound card for a
        computer: <a href="kb/open-questions.html">open questions</a>.</p>
    </main>`;
  }

  function renderHelp() {
    view.innerHTML = `<main class="prose">
      <h2>Add a project</h2>
      <p>Anything that runs on, or is built for, the TrimUI Brick, Brick Hammer or Brick Pro and has its source on GitHub.
        Use the <a href="${REPO}/issues/new?template=add-project.yml">add a project</a> form, or add an entry to
        <code>data/projects.yml</code> in a pull request. The three-day check also searches GitHub and the NextUI Pak Store
        for new projects on its own.</p>
      <h2>Correct an entry</h2>
      <p>Wrong category, firmware or device? Use the <a href="${REPO}/issues/new?template=correction.yml">correction</a>
        form or edit <code>data/projects.yml</code>. Version, licence, last commit and stars are read from the repo
        automatically; to change those, change the repo.</p>
      <h2>Make your project count as open source here</h2>
      <p>Add a <code>LICENSE</code> file and keep the source in the repo. Entries without them carry a “no licence”,
        “no source” or “no repo” mark and disappear when visitors tick “open source only”.</p>
      <h2>Share what you found out</h2>
      <p>Hardware facts, latency numbers, firmware quirks: open a pull request against <code>knowledge/</code> with a source
        for each fact, or ask in <a href="${REPO}/discussions/categories/q-a">Q&amp;A</a>.</p>
      <h2>How it stays current</h2>
      <p>Every three days a GitHub Action reads each repo (latest commit, tags, licence, <code>pak.json</code>), refreshes
        stars and descriptions, searches for new projects and rebuilds this page; a maintainer run then reviews what
        changed and sorts new finds in. Last check: ${esc(DATA.checked)}. Details in
        <a href="${REPO}/blob/main/docs/UPDATING.md">docs/UPDATING.md</a>.</p>
    </main>`;
  }

  function themeButtons() {
    let cur = "auto";
    try { cur = localStorage.getItem("ba-theme") || "auto"; } catch (e) {}
    if (cur === "pink" || cur === "brick") cur = "light";
    document.querySelectorAll("#themes button").forEach(b => {
      b.classList.toggle("on", b.dataset.theme === cur);
      b.onclick = () => {
        const t = b.dataset.theme;
        if (t === "auto") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = t;
        try { localStorage.setItem("ba-theme", t); } catch (e) {}
        themeButtons();
      };
    });
  }
  themeButtons();

  const R = { projects: renderProjects, new: renderNew, dev: renderDev, ask: renderAsk, help: renderHelp };
  function show() {
    document.querySelectorAll("#tabs button").forEach(b => b.classList.toggle("on", b.dataset.t === state.t));
    (R[state.t] || renderProjects)();
    saveUrl();
  }
  document.querySelectorAll("#tabs button").forEach(b => b.onclick = () => { state.t = b.dataset.t; show(); window.scrollTo(0, 0); });

  Promise.all([load("export/projects.json", null), load("export/news.json", []), load("export/discussions.json", [])]).then(([d, n, x]) => {
    if (!d) { view.innerHTML = '<main class="empty">Could not load export/projects.json.</main>'; return; }
    DATA = d; NEWS = n || []; DISC = x || [];
    $("#n-projects").textContent = d.projects.filter(p => p.activity === "active" || p.activity === "quiet").length;
    $("#checked").textContent = `Checked every three days (last ${d.checked}).`;
    show();
  });
})();
