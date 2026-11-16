"""
Objective 5, Step 5: automated accessibility scan of the kiosk UI.

Starts the app with the stand-in model (the UI is the same with the real models), drives it into each state the
design scenarios reach, and scans the page in every state:
  Lab: welcome; after a shopping turn (product cards, quick replies); tool-call drawer; stage drawer; a picker menu
  open; Custom switches with the untested banner; compare mode after a turn. Kiosk: welcome; after a shopping turn.
Rule (design doc, Step 5): no serious or critical issue.

The scanner is axe-core when it is available (pip install axe-playwright-python, or AXE_JS=path\\to\\axe.min.js),
the standard automated checker. Otherwise a built-in scan runs the checks behind axe's serious and critical rules
that apply to this page: accessible names (buttons, links, form fields, images), colour contrast (WCAG AA), duplicate
ids, document language and title, valid ARIA roles and states, and whether every focusable control can be reached
and shows a visible focus ring.

    python app\\a11y_check.py            # writes results_obj5/_a11y_step5/report.md and report.json
"""
import argparse
import json
import os
import socket
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

BUILTIN = r"""
() => {
  const out = [];
  const add = (rule, impact, el, msg) => out.push({rule, impact, target: sel(el), msg});
  const sel = el => { if (!el || !el.tagName) return ""; if (el.id) return "#" + el.id;
    let s = el.tagName.toLowerCase(); if (el.className && typeof el.className === "string") s += "." + el.className.trim().split(/\s+/).join(".");
    return s; };
  const visible = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none" && !el.closest("[hidden]"); };
  const name = el => {
    const lb = el.getAttribute("aria-labelledby");
    if (lb) return lb.split(/\s+/).map(i => (document.getElementById(i) || {}).textContent || "").join(" ").trim();
    if (el.getAttribute("aria-label")) return el.getAttribute("aria-label").trim();
    if (el.labels && el.labels.length) return [...el.labels].map(l => l.textContent).join(" ").trim();
    if (el.tagName === "IMG") return (el.getAttribute("alt") || "").trim();
    const t = (el.innerText || el.textContent || "").trim();
    if (t) return t;
    const img = el.querySelector("img[alt]"); if (img) return img.alt.trim();
    return (el.getAttribute("title") || "").trim();
  };
  // document
  if (!document.documentElement.lang) add("html-has-lang", "serious", document.documentElement, "no lang attribute");
  if (!document.title.trim()) add("document-title", "serious", document.documentElement, "empty title");
  // names
  for (const el of document.querySelectorAll("button, a[href], [role=button], [role=menuitem], [role=tab], [role=switch], [role=checkbox]"))
    if (visible(el) && !name(el)) add("button-name", "critical", el, "control has no accessible name");
  for (const el of document.querySelectorAll("input:not([type=hidden]), textarea, select"))
    if (visible(el) && !name(el)) add("label", "critical", el, "form field has no label");
  for (const el of document.querySelectorAll("img"))
    if (visible(el) && !el.hasAttribute("alt") && el.getAttribute("role") !== "presentation") add("image-alt", "critical", el, "image has no alt");
  // ids
  const ids = {}; for (const el of document.querySelectorAll("[id]")) ids[el.id] = (ids[el.id] || 0) + 1;
  for (const [k, n] of Object.entries(ids)) if (n > 1) add("duplicate-id-aria", "critical", document.getElementById(k), `id '${k}' used ${n} times`);
  for (const el of document.querySelectorAll("[aria-labelledby],[aria-controls],[aria-describedby]"))
    for (const a of ["aria-labelledby", "aria-controls", "aria-describedby"]) { const v = el.getAttribute(a);
      if (v) for (const i of v.split(/\s+/)) if (!document.getElementById(i)) add("aria-valid-attr-value", "critical", el, `${a} points to missing id '${i}'`); }
  // roles
  const ROLES = new Set(["button","menu","menuitem","menuitemradio","menuitemcheckbox","tab","tablist","tabpanel","switch","checkbox","status","log","alert","dialog","region","navigation","main","list","listitem","presentation","none","group","img","heading","note","separator","toolbar","tooltip","complementary","banner","contentinfo","search","form","article","progressbar","radio","radiogroup","textbox","option","listbox","combobox","grid","row","cell","table","rowheader","columnheader","link"]);
  for (const el of document.querySelectorAll("[role]")) for (const r of el.getAttribute("role").split(/\s+/))
    if (!ROLES.has(r)) add("aria-roles", "critical", el, `invalid role '${r}'`);
  for (const el of document.querySelectorAll("[role=menu]")) if (visible(el) && !el.querySelector("[role^=menuitem]"))
    add("aria-required-children", "critical", el, "menu without menu items");
  for (const el of document.querySelectorAll("[role^=menuitem]")) if (!el.closest("[role=menu],[role=menubar],[role=group]"))
    add("aria-required-parent", "critical", el, "menu item outside a menu");
  for (const el of document.querySelectorAll("[role=tab]")) if (!el.closest("[role=tablist]"))
    add("aria-required-parent", "critical", el, "tab outside a tablist");
  for (const el of document.querySelectorAll("[role=switch],[role=checkbox]")) if (!el.hasAttribute("aria-checked") && el.tagName !== "INPUT")
    add("aria-required-attr", "critical", el, "switch without aria-checked");
  // contrast
  const rgb = s => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(",").map(x => parseFloat(x)); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1}; };
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b); };
  const bgOf = el => { let cs, layers = []; for (let e = el; e; e = e.parentElement) { cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== "none") return null;
      const c = rgb(cs.backgroundColor); if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; } }
    let base = {r:255,g:255,b:255}; for (const c of layers.reverse()) base = {r:c.r*c.a+base.r*(1-c.a), g:c.g*c.a+base.g*(1-c.a), b:c.b*c.a+base.b*(1-c.a)};
    return base; };
  const seen = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const el = n.parentElement; if (!el || seen.has(el) || !n.textContent.trim() || !visible(el)) continue;
    seen.add(el);
    if (el.closest("button[disabled], [aria-disabled=true], textarea, input, select, option")) continue;
    const cs = getComputedStyle(el), fg = rgb(cs.color), bg = bgOf(el); if (!fg || !bg) continue;
    const opacity = [...function*(){ for (let e = el; e; e = e.parentElement) yield parseFloat(getComputedStyle(e).opacity); }()].reduce((a, b) => a * b, 1);
    const f = {r: fg.r*fg.a*opacity + bg.r*(1-fg.a*opacity), g: fg.g*fg.a*opacity + bg.g*(1-fg.a*opacity), b: fg.b*fg.a*opacity + bg.b*(1-fg.a*opacity)};
    const L1 = lum(f), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700;
    const need = (size >= 24 || (bold && size >= 18.66)) ? 3 : 4.5;
    if (ratio < need) add("color-contrast", "serious", el, `contrast ${ratio.toFixed(2)}:1 (needs ${need}:1) for '${n.textContent.trim().slice(0, 40)}'`);
  }
  return out;
}
"""

FOCUS = r"""
() => {
  const a = document.activeElement; if (!a || a === document.body) return null;
  const cs = getComputedStyle(a);
  const has = c => (c.outlineStyle !== "none" && parseFloat(c.outlineWidth) > 0) || (c.boxShadow && c.boxShadow !== "none");
  let ring = has(cs);
  for (let e = a.parentElement, i = 0; !ring && e && i < 2; e = e.parentElement, i++)   // a ring on the field's box
    ring = e.matches(":focus-within") && has(getComputedStyle(e));
  let s = a.tagName.toLowerCase() + (a.id ? "#" + a.id : "") + (a.className && typeof a.className === "string" ? "." + a.className.split(" ")[0] : "");
  return {target: s, ring};
}
"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def axe_scan(page):
    path = os.environ.get("AXE_JS")
    src = None
    if path and os.path.exists(path):
        src = open(path, encoding="utf-8").read()
    else:
        try:
            import axe_playwright_python
            d = os.path.dirname(axe_playwright_python.__file__)
            for dp, _, fs in os.walk(d):
                if "axe.min.js" in fs:
                    src = open(os.path.join(dp, "axe.min.js"), encoding="utf-8").read()
                    break
        except ImportError:
            pass
    if not src:
        return None
    page.evaluate(src)
    res = page.evaluate("async () => await axe.run(document, {resultTypes: ['violations']})")
    out = []
    for v in res["violations"]:
        for n in v["nodes"]:
            out.append({"rule": v["id"], "impact": v.get("impact") or "minor", "target": " ".join(n["target"]),
                        "msg": v["help"]})
    return out


def scan(page, use_axe):
    if use_axe:
        r = axe_scan(page)
        if r is not None:
            return r, "axe-core"
    return page.evaluate(BUILTIN), "built-in"


def keyboard(page, n=40):
    """Tab through the page: every stop must show a focus ring."""
    page.evaluate("document.activeElement && document.activeElement.blur()")
    out, seen = [], set()
    for _ in range(n):
        page.keyboard.press("Tab")
        f = page.evaluate(FOCUS)
        if not f or f["target"] in seen:
            continue
        seen.add(f["target"])
        if not f["ring"]:
            out.append({"rule": "focus-visible", "impact": "serious", "target": f["target"], "msg": "no visible focus"})
    return out, len(seen)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-axe", action="store_true", help="use the built-in scan even if axe-core is available")
    a = ap.parse_args(argv)
    from playwright.sync_api import sync_playwright
    from app import server as app_server
    tmp = tempfile.mkdtemp()
    results, engine_used = [], set()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for mode in ("lab", "kiosk"):
            svc = app_server.make_service(mode, "A", fake=True, llama_port=free_port(), log_dir=tmp)
            port = free_port()
            httpd = app_server.serve(svc, port=port)
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            svc.prepare()
            pg = b.new_page(viewport={"width": 1280, "height": 860})
            pg.goto(f"http://127.0.0.1:{port}/")
            pg.wait_for_selector(".welcome")
            states = []

            def snap(state):
                v, eng = scan(pg, not a.no_axe)
                engine_used.add(eng)
                states.append(state)
                for x in v:
                    results.append(dict(x, mode=mode, state=state))

            snap("welcome")
            kb, stops = keyboard(pg)
            for x in kb:
                results.append(dict(x, mode=mode, state="keyboard"))
            pg.fill("#input", "Formal watch for my father under 15000")
            pg.keyboard.press("Enter")
            pg.wait_for_selector(".card", timeout=30000)
            pg.wait_for_timeout(500)
            snap("after a shopping turn (cards, quick replies)")
            if mode == "lab":
                pg.click("#tab-tools")
                pg.wait_for_selector(".call")
                snap("tool-call drawer")
                pg.click("#dtab-stages")
                pg.wait_for_selector(".wf")
                snap("stage drawer")
                pg.click("#drawer-close")
                pg.click("#chip-pipeline")
                pg.wait_for_selector("#menu-pipeline button")
                snap("pipeline menu open")
                pg.click("#menu-pipeline button:has-text('Custom')")
                pg.wait_for_selector("#custom-panel .toggle")
                pg.uncheck("#tg-retrieval")
                pg.wait_for_selector("#untested", state="visible")
                snap("Custom switches, untested banner")
                pg.click("#chip-compare")
                pg.wait_for_selector(".compare .col-label:not(:empty)")
                pg.fill("#input", "Do you offer gift wrapping?")
                pg.keyboard.press("Enter")
                pg.wait_for_function("document.querySelectorAll('.compare .msg.bot .meta button').length >= 2",
                                     timeout=60000)
                snap("compare mode after a turn")
            pg.close()
            httpd.shutdown()
            httpd.server_close()
            svc.close()
            results.append({"rule": "_states", "impact": "none", "target": "", "msg": f"{len(states)} states, "
                            f"{stops} keyboard stops", "mode": mode, "state": ""})
        b.close()
    real = [r for r in results if r["rule"] != "_states"]
    bad = [r for r in real if r["impact"] in ("serious", "critical")]
    od = os.path.join(ROOT, "results_obj5", "_a11y_step5")
    os.makedirs(od, exist_ok=True)
    L = ["# Objective 5, Step 5: accessibility scan", "",
         f"Scanner: {', '.join(sorted(engine_used))}. Rule: no serious or critical issue.", ""]
    for r in results:
        if r["rule"] == "_states":
            L.append(f"- {r['mode']}: {r['msg']}")
    L += ["", f"**Serious or critical issues: {len(bad)}** -> {'met' if not bad else 'NOT met'}", ""]
    if real:
        L += ["| Mode | State | Impact | Rule | Element | Detail |", "|---|---|---|---|---|---|"]
        for r in real:
            L.append(f"| {r['mode']} | {r['state']} | {r['impact']} | {r['rule']} | `{r['target']}` | {r['msg']} |")
    with open(os.path.join(od, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(od, "report.json"), "w", encoding="utf-8") as f:
        json.dump({"scanner": sorted(engine_used), "serious_or_critical": len(bad), "issues": real}, f, indent=1,
                  ensure_ascii=False)
    print("\n".join(L))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
