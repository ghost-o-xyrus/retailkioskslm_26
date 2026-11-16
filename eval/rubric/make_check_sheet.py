"""
Make the human check sheet: 20 random blind replies from packet.json, no model names, no judge scores.

    python eval/rubric/make_check_sheet.py eval/rubric/stage3
Writes human_check.xlsx (fill the Score columns 1–5, or leave blank for not applicable) and human_check_key.json.
"""
import json, os, random, sys
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation


def tools_text(calls):
    if not calls:
        return "(no tool calls)"
    out = []
    for c in calls:
        out.append(f"{c['name']}({json.dumps(c['arguments'], ensure_ascii=False)})")
        try:
            r = json.loads(c["result"])
        except Exception:
            out.append("  → " + str(c["result"])[:800])
            continue
        items = r.get("results") if isinstance(r, dict) else None
        if isinstance(items, list):
            for p in items:
                bits = [p.get("product_id", ""), p.get("name", ""), f"₹{p['mrp']}" if "mrp" in p else "",
                        f"{p['case_diameter_mm']} mm" if p.get("case_diameter_mm") else "",
                        f"{p['water_resistance_m']} m WR" if p.get("water_resistance_m") else "",
                        p.get("movement", ""),
                        "in stock here" if p.get("in_stock_here") else ("not in stock here" if "in_stock_here" in p else "")]
                out.append("  → " + " | ".join(b for b in bits if b))
        else:
            out.append("  → " + json.dumps(r, ensure_ascii=False)[:1200])
    return "\n".join(out)


def main(folder, n=20, seed=19):
    packet = json.load(open(os.path.join(folder, "packet.json"), encoding="utf-8"))
    rng = random.Random(seed)
    picks = [(p, rng.choice("XY")) for p in rng.sample(packet, n)]
    wb = Workbook()
    ws = wb.active
    ws.title = "Check"
    head = ["Check ID", "Conversation", "What the tools returned", "Reply to score"]
    for i in range(1, 5):
        head += [f"Rubric {i}", f"Score {i}"]
    ws.append(head)
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)
    ws.add_data_validation(dv)
    key = {}
    for k, (p, label) in enumerate(picks, 1):
        cid = f"S{k:02d}"
        key[cid] = {"item": p["item"], "label": label}
        conv = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in p["conversation"])
        if p.get("provided_information"):
            conv = "PRODUCT INFORMATION GIVEN TO THE ASSISTANT:\n" + p["provided_information"] + "\n\n" + conv
        rep = p["replies"][label]
        row = [cid, conv, tools_text(rep["tool_calls"]), rep["final_reply"]]
        for line in p["rubric"]:
            row += [line, None]
        ws.append(row)
        for col in (6, 8, 10, 12):
            dv.add(ws.cell(row=k + 1, column=col))
    widths = [8, 40, 60, 60] + [28, 8] * 4
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
    fill = PatternFill("solid", fgColor="FFF2CC")
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for col in (6, 8, 10, 12):
            row[col - 1].fill = fill
    for c in ws[1]:
        c.font = Font(bold=True)
    ws.freeze_panes = "B2"
    g = wb.create_sheet("How to score")
    for line in ["Score each rubric line 1–5 for the reply in that row (yellow cells).",
                 "5 fully meets the line · 4 one minor slip · 3 partly · 2 mostly fails · 1 fails or contradicts it.",
                 "Grounding lines: a product, ID, price or spec in the reply that is not in 'What the tools returned' scores 2 or lower.",
                 "Leave a cell blank only if the line truly cannot apply to that reply. An empty or '(no reply)' reply scores 1 on every line.",
                 "Score each reply on its own. Do not look at the judge's scores first."]:
        g.append([line])
    g.column_dimensions["A"].width = 120
    wb.save(os.path.join(folder, "human_check.xlsx"))
    json.dump(key, open(os.path.join(folder, "human_check_key.json"), "w"), indent=1)
    print("wrote human_check.xlsx with", n, "replies")


if __name__ == "__main__":
    main(sys.argv[1])
