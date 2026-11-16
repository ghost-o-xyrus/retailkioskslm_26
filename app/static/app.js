/* Objective 5, Step 5: the kiosk app's frontend. Plain JavaScript, no build step, no network beyond the local app.
   Layout and behaviour follow the design doc: picker (tier, model, pipeline, adapter, switches), compare mode,
   chat with product cards and quick replies, the tool-call and stage drawers, a disabled mic, Kiosk mode. */
"use strict";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const S = {
  cfg: null, sel: null, sid: null, compare: { on: false, id: null, a: null, b: null },
  traces: {}, live: {}, selected: null, drawer: null, busy: false, lastInput: Date.now(),
};
const IDLE_MS = 120000;

function el(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (v === true) e.setAttribute(k, "");
    else if (v !== false && v != null) e.setAttribute(k, v);
  }
  for (const k of kids) if (k != null) e.append(k);
  return e;
}
const rs = n => n == null ? "" : "Rs " + Number(n).toLocaleString("en-IN");
const sec = ms => ms == null ? "–" : (ms / 1000).toFixed(ms < 10000 ? 1 : 0) + " s";

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}

async function stream(path, body, onEvent) {
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.error || r.statusText); }
  const reader = r.body.getReader(), dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
      for (const line of chunk.split("\n")) if (line.startsWith("data: ")) {
        try { onEvent(JSON.parse(line.slice(6))); } catch (e) { console.error(e); }
      }
    }
  }
}

/* ---------------- configuration picker ---------------- */
const tierOf = id => S.cfg.tiers.find(t => t.id === id);
const modelOf = id => S.cfg.models.find(m => m.id === id);
const pipeOf = id => S.cfg.pipelines.find(p => p.id === id);

function closeMenus() { $$(".menu.open").forEach(m => m.classList.remove("open")); }
function menu(id, items) {
  const m = $("#" + id); m.innerHTML = "";
  for (const it of items) {
    const b = el("button", { role: "menuitem", class: it.sel ? "sel" : "", disabled: it.disabled || false,
      onclick: e => { e.stopPropagation(); closeMenus(); it.pick(); } },
      el("span", { text: it.label }), it.hint ? el("span", { class: "opt-hint", text: it.hint }) : null,
      it.ev ? el("span", { class: "opt-ev", text: it.ev }) : null);
    m.append(b);
  }
}
function wireChip(chipId, menuId) {
  $("#" + chipId).addEventListener("click", e => {
    e.stopPropagation();
    const m = $("#" + menuId), open = m.classList.contains("open");
    closeMenus(); if (!open) m.classList.add("open");
  });
}

function renderPicker() {
  const s = S.sel, t = tierOf(s.tier), m = modelOf(s.model), p = pipeOf(s.pipeline);
  $("#chip-tier").textContent = `${t.label} · ${t.hint.split(",")[0]}`;
  $("#chip-model").textContent = m.label;
  $("#chip-pipeline").textContent = "Pipeline: " + p.label;
  $("#chip-adapter").textContent = "Adapter: " + (s.adapter === "none" ? "none" : s.adapter);
  menu("menu-tier", S.cfg.tiers.map(x => ({ label: x.label, hint: x.hint, sel: x.id === s.tier,
    pick: () => { const keep = modelOf(s.model).tiers.includes(x.id);
      setSel({ tier: x.id, model: keep ? s.model : S.cfg.models.find(mm => mm.deployed_on === x.id).id, adapter: "none" }); } })));
  menu("menu-model", S.cfg.models.map(x => ({ label: x.label + (x.available ? "" : " (file not found)"),
    hint: x.deployed_on === s.tier ? "deployed on this tier" : (x.tiers.includes(s.tier) ? "" : "does not run on this tier"),
    sel: x.id === s.model, disabled: !x.available || !x.tiers.includes(s.tier),
    pick: () => setSel({ model: x.id, adapter: "none" }) })));
  menu("menu-pipeline", S.cfg.pipelines.map(x => ({ label: x.label, hint: x.hint, ev: x.evidence, sel: x.id === s.pipeline,
    pick: () => setSel({ pipeline: x.id }) })));
  const ads = (m.adapters || []);
  menu("menu-adapter", [{ label: "None", sel: s.adapter === "none", pick: () => setSel({ adapter: "none" }) }]
    .concat(["lora", "qlora"].map(a => ({ label: a === "lora" ? "LoRA" : "QLoRA",
      hint: ads.includes(a) ? "Objective 4 adapter, loaded next to the model file" : "no adapter file yet",
      disabled: !ads.includes(a), sel: s.adapter === a, pick: () => setSel({ adapter: a }) }))));
  $("#chip-adapter").disabled = !ads.length;
  renderCustom();
}

function renderCustom() {
  const panel = $("#custom-panel");
  panel.hidden = S.sel.pipeline !== "custom" || S.compare.on;
  if (panel.hidden) return;
  panel.innerHTML = "";
  for (const t of S.cfg.toggles) {
    const v = S.sel.toggles[t.id];
    let ctl;
    if (t.kind === "bool") {
      ctl = el("input", { type: "checkbox", id: "tg-" + t.id, checked: !!v,
        onchange: e => setSel({ toggles: { ...S.sel.toggles, [t.id]: e.target.checked } }) });
    } else {
      ctl = el("select", { id: "tg-" + t.id, onchange: e => setSel({ toggles: { ...S.sel.toggles, [t.id]: e.target.value } }) },
        ...t.choices.map(c => el("option", { value: c, selected: c === v, text: c })));
    }
    panel.append(el("div", { class: "toggle" }, el("label", { for: "tg-" + t.id }, ctl, t.label),
      el("span", { class: "ev", text: t.hint }), t.evidence ? el("span", { class: "ev", text: t.evidence }) : null));
  }
}

async function setSel(patch) {
  const next = { ...S.sel, ...patch };
  // a new model starts from that model's own O3-final switches (the 4B ran without short replies)
  if (patch.model && patch.model !== S.sel.model && S.cfg.toggle_defaults_by_model)
    next.toggles = { ...S.cfg.toggle_defaults_by_model[patch.model] };
  try {
    const r = await api(`/api/sessions/${S.sid}/config`, { method: "POST", body: { selection: next } });
    S.sel = r.selection; showUntested(r.untested);
    renderPicker(); notice(`Now using ${r.label}`);
  } catch (e) { notice(e.message, true); renderPicker(); }
}
function showUntested(u) { $("#untested").hidden = !u; }

/* ---------------- sessions ---------------- */
async function newChat() {
  if (S.compare.on) return startCompare();
  const r = await api("/api/sessions", { method: "POST", body: { selection: S.sel } });
  S.sid = r.id; S.sel = r.selection; showUntested(r.untested);
  $("#chat-single").innerHTML = ""; welcome($("#chat-single"));
  S.selected = null; updateCounts(); renderDrawer(); refreshSessions(); renderPicker();
}
async function openSession(id) {
  const r = await api(`/api/sessions/${id}`);
  S.sid = id; S.sel = r.selection; showUntested(r.untested);
  const box = $("#chat-single"); box.innerHTML = "";
  for (const t of r.turns) {
    box.append(el("div", { class: "msg user", text: t.user }));
    const bot = botMsg(box); bot.text.textContent = t.reply || ""; renderCards(bot, t.cards || []);
    bot.meta.textContent = ""; addMeta(bot, t.turn_id, t.metrics);
    if (!S.traces[t.turn_id]) S.traces[t.turn_id] = await api(`/api/turns/${t.turn_id}/trace`).catch(() => null);
  }
  if (!r.turns.length) welcome(box);
  refreshSessions(); renderPicker();
}
async function refreshSessions() {
  if (S.cfg.mode === "kiosk") return;
  const list = await api("/api/sessions");
  const ul = $("#session-list"); ul.innerHTML = "";
  for (const s of list) ul.append(el("li", {}, el("button", { class: s.id === S.sid ? "sel" : "", title: s.label,
    onclick: () => openSession(s.id), text: s.title })));
}

/* ---------------- chat rendering ---------------- */
function welcome(box) {
  box.append(el("div", { class: "welcome" },
    el("p", { text: `Welcome to ${S.cfg.brand}. Ask about our watches, or tell me who you are shopping for.` })));
}
function botMsg(box) {
  const wrap = el("div", { class: "msg bot" });
  const status = el("div", { class: "msg status", text: "" });
  const text = el("div", { class: "text" });
  const cards = el("div", { class: "cards" });
  const quick = el("div", { class: "quick" });
  const meta = el("div", { class: "meta" });
  wrap.append(status, text, cards, quick, meta);
  box.append(wrap); box.scrollTop = box.scrollHeight;
  return { wrap, status, text, cards, quick, meta, box };
}
const WATCH_SVG = '<svg width="48" height="48" viewBox="0 0 48 48" aria-hidden="true"><rect x="18" y="2" width="12" height="10" rx="2" fill="currentColor" opacity=".35"/><rect x="18" y="36" width="12" height="10" rx="2" fill="currentColor" opacity=".35"/><circle cx="24" cy="24" r="13" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M24 16v8l5 3" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>';
function renderCards(bot, cards) {
  bot.cards.innerHTML = ""; bot.quick.innerHTML = "";
  for (const c of cards) {
    let img;
    if (c.image) {
      img = el("div", { class: "img has-photo" + (c.images ? " large" : "") });
      const main = el("img", { src: c.image, alt: c.image_alt || c.name, loading: "lazy" });
      img.append(main);
      if (c.images && c.images.length > 1) {
        const thumbs = el("div", { class: "thumbs", role: "group", "aria-label": "Views" });
        c.images.forEach((im, i) => thumbs.append(el("button", { class: "thumb" + (i === 0 ? " sel" : ""),
          "aria-label": "Show the " + im.view + " view", "aria-pressed": i === 0 ? "true" : "false",
          onclick: e => { main.src = im.url; main.alt = im.alt;
            thumbs.querySelectorAll(".thumb").forEach(b => { b.classList.remove("sel"); b.setAttribute("aria-pressed", "false"); });
            e.currentTarget.classList.add("sel"); e.currentTarget.setAttribute("aria-pressed", "true"); } },
          el("img", { src: im.url, alt: "" }))));
        img.append(thumbs);
      }
    } else {
      img = el("div", { class: "img", role: "img",
        "aria-label": `${c.name}${c.dial_colour ? ", " + c.dial_colour + " dial" : ""}${c.strap ? ", " + c.strap + " strap" : ""} (no picture yet)` });
      img.innerHTML = WATCH_SVG;
    }
    bot.cards.append(el("div", { class: "card" + (c.images ? " gallery" : "") }, img,
      el("div", { class: "name", text: c.design || c.name }),
      el("div", { class: "sub", text: `${c.product_id} · ${rs(c.mrp)}` }),
      el("div", { class: "sub", text: [c.dial_colour && c.dial_colour + " dial", c.strap].filter(Boolean).join(", ") }),
      c.in_stock_here == null ? null : el("span", { class: "badge " + (c.in_stock_here ? "in" : "out"),
        text: c.in_stock_here ? "In stock here" : "Not in stock here" })));
  }
  const q = [];
  if (cards.length >= 2) q.push([`Compare 1 and 2`, `Compare ${cards[0].product_id} and ${cards[1].product_id}`]);
  if (cards.length) q.push(["Show more", "Show me a few more options like these"]);
  if (cards.length) q.push(["Call staff", "Can a staff member help me with this?"]);
  for (const [label, text] of q) bot.quick.append(el("button", { text: label, onclick: () => send(text) }));
}
function addMeta(bot, turnId, m) {
  bot.meta.innerHTML = "";
  if (m && S.cfg.mode !== "kiosk") bot.meta.append(el("span", { text: `first word ${sec(m.first_visible_ms)} · total ${sec(m.end_to_end_ms)}` }));
  if (S.cfg.mode !== "kiosk" && turnId) {
    bot.meta.append(el("button", { text: "Tool calls", onclick: () => { S.selected = turnId; showDrawer("tools"); } }));
    bot.meta.append(el("button", { text: "Stages", onclick: () => { S.selected = turnId; showDrawer("stages"); } }));
  }
}
function notice(text, bad) {
  const box = S.compare.on ? $(".compare .chat[data-side=a]") : $("#chat-single");
  box.append(el("div", { class: "msg status" + (bad ? " error" : ""), text }));
  box.scrollTop = box.scrollHeight;
}

/* ---------------- sending ---------------- */
async function send(text) {
  text = (text || "").trim();
  if (!text || S.busy) return;
  S.busy = true; S.lastInput = Date.now(); $("#send").disabled = true;
  $("#input").value = ""; autosize();
  const boxes = S.compare.on ? { a: $(".compare .chat[data-side=a]"), b: $(".compare .chat[data-side=b]") }
                             : { _: $("#chat-single") };
  const bots = {};
  for (const [k, box] of Object.entries(boxes)) {
    $(".welcome", box)?.remove();
    box.append(el("div", { class: "msg user", text }));
    bots[k] = botMsg(box);
    bots[k].status.textContent = S.compare.on && k === "b" ? "Waiting for A to finish…" : "…";
    S.live[k] = { tools: [] };
  }
  const path = S.compare.on ? `/api/compare/${S.compare.id}/turns` : `/api/sessions/${S.sid}/turns`;
  try {
    await stream(path, { message: text }, ev => {
      const k = ev.side || "_", bot = bots[k];
      if (!bot) return;
      switch (ev.type) {
        case "status": bot.status.textContent = ev.text; break;
        case "round_start": bot.streamed = ""; break;
        case "token":
          bot.streamed = (bot.streamed || "") + ev.text;
          bot.text.textContent = bot.streamed; bot.status.textContent = ""; break;
        case "model_loaded": bot.status.textContent = `Model loaded in ${sec(ev.load_ms)}`; break;
        case "tool_call": S.live[k].tools.push(ev); break;
        case "final": bot.text.textContent = ev.reply || ""; bot.status.textContent = ""; break;
        case "metrics": bot.metrics = ev; break;
        case "cards": renderCards(bot, ev.cards || []); break;
        case "turn_end":
          S.live[ev.turn_id] = S.live[k];
          api(`/api/turns/${ev.turn_id}/trace`).then(tr => {
            S.traces[ev.turn_id] = tr; S.selected = ev.turn_id; addMeta(bot, ev.turn_id, tr.metrics);
            if (S.compare.on) $(`.col-label[data-side=${k}]`).textContent = ev.label;
            updateCounts(); renderDrawer(); renderStrip();
          });
          break;
        case "error": bot.status.textContent = ""; bot.text.textContent = ev.message; bot.wrap.classList.add("error"); break;
      }
      bot.box.scrollTop = bot.box.scrollHeight;
    });
  } catch (e) {
    for (const bot of Object.values(bots)) { bot.status.textContent = ""; bot.text.textContent = "Sorry, the kiosk could not answer: " + e.message; }
  }
  S.busy = false; $("#send").disabled = false; $("#input").focus();
  refreshSessions();
}

/* ---------------- drawers ---------------- */
function updateCounts() {
  const tr = S.traces[S.selected];
  $("#tools-count").textContent = tr ? `(${(tr.tool_calls || []).length})` : "";
  $("#stages-count").textContent = tr && tr.metrics ? `· ${sec(tr.metrics.end_to_end_ms)}` : "";
}
function openDrawer(kind) {          // the bottom tabs: open, or close if already showing this one
  showDrawer(S.drawer === kind && !$("#drawer").hidden ? null : kind);
}
function showDrawer(kind) {
  S.drawer = kind;
  $("#drawer").hidden = !S.drawer;
  $("#tab-tools").setAttribute("aria-expanded", S.drawer === "tools");
  $("#tab-stages").setAttribute("aria-expanded", S.drawer === "stages");
  renderDrawer();
}
function renderDrawer() {
  if (!S.drawer) return;
  const tr = S.traces[S.selected], body = $("#drawer-body");
  $("#dtab-tools").setAttribute("aria-selected", S.drawer === "tools");
  $("#dtab-stages").setAttribute("aria-selected", S.drawer === "stages");
  $("#drawer-turn").textContent = tr ? `${tr.config || ""} · turn ${tr.turn}` : "";
  body.innerHTML = "";
  if (!tr) { body.append(el("p", { class: "quiet", text: "Send a message, then open this to see what happened." })); return; }
  S.drawer === "tools" ? renderTools(tr, body) : renderStages(tr, body);
}
function renderTools(tr, body) {
  const calls = tr.tool_calls || [], live = (S.live[tr.turn_id] || { tools: [] }).tools;
  if (!calls.length) body.append(el("p", { class: "quiet", text: "No tool calls in this turn." }));
  calls.forEach((c, i) => {
    const seen = live.find(x => x.id === c.id && x.name === c.name);
    const who = c.by === "harness" ? "harness" : (c.guard ? "guard" : "model");
    const raw = el("pre", { text: JSON.stringify(c.result, null, 2) }); raw.hidden = true;
    body.append(el("div", { class: "call" },
      el("div", { class: "who " + who, text: `${i + 1}. ${who}${c.harness_note ? " · " + c.harness_note : ""}${c.guard ? " · " + c.guard : ""}` }),
      el("strong", { text: c.name }),
      el("pre", { text: JSON.stringify(c.arguments) }),
      el("div", { class: "quiet", text: "Result as the model saw it:" }),
      el("pre", { text: seen ? seen.result : JSON.stringify(c.result) }),
      el("button", { class: "quiet", text: "Raw JSON", onclick: () => { raw.hidden = !raw.hidden; } }), raw));
  });
  if ((tr.flags || []).length) body.append(el("p", { class: "quiet", text: "Flags: " + tr.flags.join(", ") }));
}
function renderStages(tr, body) {
  const m = tr.metrics || {}, st = tr.stages || [];
  const total = m.end_to_end_ms || st.reduce((a, s) => Math.max(a, s.start_ms + s.ms), 0) || 1;
  const toks = (tr.turns || []).reduce((a, t) => [a[0] + (t.prompt_tokens || 0), a[1] + (t.predicted_n || 0)], [0, 0]);
  const peak = st.reduce((a, s) => Math.max(a, Object.values(s.peak_mb || {}).reduce((x, y) => x + (y || 0), 0)), 0);
  body.append(el("div", { class: "chips" },
    el("span", { text: `First word ${sec(m.first_visible_ms)}` }), el("span", { text: `Total ${sec(m.end_to_end_ms)}` }),
    el("span", { text: `Tokens read ${toks[0]} · written ${toks[1]}` }),
    el("span", { text: `Writing ${m.tokens_per_s ? m.tokens_per_s.toFixed(1) + " tokens/s" : "–"}` }),
    el("span", { text: `Peak RAM ${peak ? (peak / 1024).toFixed(2) + " GB" : "–"}` }),
    tr.stage_summary ? el("span", { text: `Unattributed ${tr.stage_summary.unattributed_ms} ms` }) : null));
  if (!st.length) { body.append(el("p", { class: "quiet", text: "No stage log for this turn (stage clock off)." })); return; }
  const wf = el("div", { class: "wf" });
  for (const s of st) {
    const left = 100 * s.start_ms / total, w = Math.max(0.3, 100 * s.ms / total);
    const info = s.info ? Object.entries(s.info).filter(([, v]) => v != null && v !== "").map(([k, v]) => `${k}: ${v}`).join(", ") : "";
    wf.append(el("div", { text: s.stage.replace("_", " ") + (s.info && s.info.round != null ? ` ${s.info.round + 1}` : ""), title: info }));
    const track = el("div", { class: "track" }); const bar = el("div", { class: "bar" });
    bar.style.left = Math.min(99.5, left) + "%"; bar.style.width = Math.min(w, 100 - Math.min(99.5, left)) + "%"; track.append(bar); wf.append(track);
    wf.append(el("div", { class: "ms", text: s.ms.toFixed(0) + " ms" }));
    let off = s.start_ms;
    for (const x of s.sub || []) {
      if (x.ms == null) continue;
      wf.append(el("div", { class: "sub-name", text: x.name + (x.tokens != null ? ` (${x.tokens} tok)` : "") }));
      const t2 = el("div", { class: "track" }); const b2 = el("div", { class: "bar sub" });
      const l2 = Math.min(99.5, 100 * off / total);
      b2.style.left = l2 + "%"; b2.style.width = Math.min(Math.max(0.3, 100 * x.ms / total), 100 - l2) + "%";
      if (x.name === "reading" || x.name === "writing") off += x.ms;
      t2.append(b2); wf.append(t2); wf.append(el("div", { class: "ms", text: x.ms.toFixed(0) + " ms" }));
    }
  }
  body.append(wf);
  const last = st[st.length - 1].rss_mb || {}, used = Object.values(last).reduce((a, b) => a + (b || 0), 0);
  const tier = tierOf((tr.selection || S.sel).tier), budget = tier && tier.ram_budget_gb;
  const ram = el("div", { class: "ram" }, el("div", { text: `RAM at the end: ${Object.entries(last).map(([k, v]) => `${k} ${(v / 1024).toFixed(2)} GB`).join(" · ")}` + (budget ? ` (budget ${budget} GB)` : "") }));
  if (budget) { const t = el("div", { class: "rtrack" }), f = el("div", { class: "rfill" + (used / 1024 > budget ? " over" : "") });
    f.style.width = Math.min(100, 100 * used / 1024 / budget) + "%"; t.append(f); ram.append(t); }
  body.append(ram);
}
function renderStrip() {
  if (!S.compare.on) { $("#strip").hidden = true; return; }
  const strip = $("#strip"); strip.hidden = false; strip.innerHTML = "";
  for (const side of ["a", "b"]) {
    const sid = S.compare[side + "Sid"], tr = Object.values(S.traces).filter(t => t.session === sid).pop();
    const m = tr && tr.metrics;
    strip.append(el("div", { text: m ? `${side.toUpperCase()}: first word ${sec(m.first_visible_ms)} · total ${sec(m.end_to_end_ms)} · ${(tr.tool_calls || []).length} tool calls` : `${side.toUpperCase()}: –` }));
  }
}

/* ---------------- compare mode ---------------- */
function combos() {
  const out = [];
  for (const t of S.cfg.tiers) for (const m of S.cfg.models) if (m.tiers.includes(t.id) && m.available)
    for (const p of S.cfg.pipelines) if (p.id !== "custom")
      out.push({ value: `${t.id}|${m.id}|${p.id}`, label: `${t.label} · ${m.label} · ${p.label}` });
  return out;
}
const parseCombo = v => { const [tier, model, pipeline] = v.split("|"); return { tier, model, pipeline, adapter: "none" }; };
async function startCompare() {
  const a = $(".cmp-sel[data-side=a]").value, b = $(".cmp-sel[data-side=b]").value;
  const r = await api("/api/compare", { method: "POST", body: { a: parseCombo(a), b: parseCombo(b) } });
  S.compare.id = r.id; S.compare.aSid = r.a.id; S.compare.bSid = r.b.id;
  $(".col-label[data-side=a]").textContent = r.a.label; $(".col-label[data-side=b]").textContent = r.b.label;
  $$(".compare .chat").forEach(c => { c.innerHTML = ""; });
  renderStrip();
}
async function toggleCompare() {
  S.compare.on = !S.compare.on;
  $("#chip-compare").setAttribute("aria-pressed", S.compare.on);
  $("#chat-single").hidden = S.compare.on; $("#chat-compare").hidden = !S.compare.on;
  if (S.compare.on) $("#untested").hidden = true;
  renderCustom();
  if (S.compare.on) {
    const opts = combos();
    for (const side of ["a", "b"]) {
      const sel = $(`.cmp-sel[data-side=${side}]`); sel.innerHTML = "";
      for (const o of opts) sel.append(el("option", { value: o.value, text: o.label }));
      sel.onchange = () => startCompare().catch(e => notice(e.message, true));
    }
    const cur = `${S.sel.tier}|${S.sel.model}|${S.sel.pipeline === "custom" ? "o3_final" : S.sel.pipeline}`;
    $(".cmp-sel[data-side=a]").value = cur;
    $(".cmp-sel[data-side=b]").value = `${S.sel.tier}|${S.sel.model}|model_only`;
    await startCompare().catch(e => notice(e.message, true));
  } else { $("#strip").hidden = true; const r = await api(`/api/sessions/${S.sid}`); showUntested(r.untested); }
}

/* ---------------- readiness: the model is loaded and warmed at start-up ---------------- */
async function waitReady() {
  let veil = null;
  for (;;) {
    let r;
    try { r = await api("/api/ready"); } catch (e) { r = { state: "loading", text: "Getting ready…" }; S.lost = true; }
    if (S.lost && r.state === "ready") {      // the app was restarted (Step 10): its chats are gone, start a new one
      S.lost = false; S.busy = false; await newChat().catch(() => { S.lost = true; });
    }
    const loading = r.state === "loading";
    $("#input").disabled = loading; $("#send").disabled = loading || S.busy;
    if (loading || r.state === "error") {
      if (!veil) { veil = el("div", { id: "ready-veil", role: "status", "aria-live": "polite" }); document.body.append(veil); }
      veil.textContent = r.state === "error" ? r.text : (r.text || "Getting ready…") + " The kiosk will be ready in a moment.";
      veil.classList.toggle("error", r.state === "error");
    } else if (veil) { veil.remove(); veil = null; }
    await new Promise(res => setTimeout(res, loading || r.state === "error" ? 1000 : 5000));
  }
}

/* ---------------- start ---------------- */
function autosize() { const t = $("#input"); t.style.height = "auto"; t.style.height = Math.min(140, t.scrollHeight) + "px"; }
async function init() {
  S.cfg = await api("/api/configs");
  document.body.className = S.cfg.mode;
  $("#brand-mark").textContent = S.cfg.brand;
  document.title = S.cfg.brand + " kiosk";
  $("#mode-tag").textContent = S.cfg.mode === "kiosk" ? "" : `Lab mode${S.cfg.fake ? " · stand-in model" : ""}`;
  $("#side-foot").textContent = S.cfg.fake ? "Stand-in model and retrieval: replies are canned." : "";
  S.sel = S.cfg.default;
  wireChip("chip-tier", "menu-tier"); wireChip("chip-model", "menu-model");
  wireChip("chip-pipeline", "menu-pipeline"); wireChip("chip-adapter", "menu-adapter");
  document.addEventListener("click", closeMenus);
  document.addEventListener("keydown", e => { if (e.key === "Escape") { closeMenus(); if (S.drawer) openDrawer(S.drawer); } });
  $("#chip-compare").addEventListener("click", () => toggleCompare());
  $("#new-chat").addEventListener("click", () => newChat());
  $("#tab-tools").addEventListener("click", () => openDrawer("tools"));
  $("#tab-stages").addEventListener("click", () => openDrawer("stages"));
  $("#drawer-close").addEventListener("click", () => openDrawer(S.drawer));
  $("#dtab-tools").addEventListener("click", () => showDrawer("tools"));
  $("#dtab-stages").addEventListener("click", () => showDrawer("stages"));
  $("#composer").addEventListener("submit", e => { e.preventDefault(); send($("#input").value); });
  $("#input").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send($("#input").value); } });
  $("#input").addEventListener("input", () => { autosize(); S.lastInput = Date.now(); });
  await newChat();
  waitReady();
  if (S.cfg.mode === "kiosk") setInterval(() => { if (!S.busy && Date.now() - S.lastInput > IDLE_MS && $(".msg.user")) { S.lastInput = Date.now(); newChat(); } }, 10000);
}
init().catch(e => { document.body.append(el("p", { class: "msg error", text: "The kiosk could not start: " + e.message })); });
