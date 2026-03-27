from __future__ import annotations

from datetime import date
from typing import Dict, List

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_ITEMS: List[Dict[str, object]] = [
    {"id": "soft_icing_cakes", "name": "Soft Icing Cakes", "price": 32},
    {"id": "fondant_icing_cakes", "name": "Fondant Icing Cakes", "price": 45},
    {"id": "cupcakes", "name": "Cupcakes (Box of 6)", "price": 18},
    {"id": "macarons", "name": "Macarons (Box of 12)", "price": 24},
    {"id": "cakepops", "name": "Cakepops (Box of 8)", "price": 16},
]
MENU_LOOKUP = {item["id"]: item for item in MENU_ITEMS}


@app.get("/")
def home():
    return render_template("index.html", menu_items=MENU_ITEMS, today=date.today().isoformat())


@app.post("/api/quote")
def quote():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    pickup_date = str(payload.get("pickupDate", "")).strip()
    size = str(payload.get("size", "Small")).strip()
    notes = str(payload.get("notes", "")).strip()
    quantities = payload.get("quantities", {})

    if not isinstance(quantities, dict):
        return jsonify({"ok": False, "message": "Invalid order payload."}), 400

    selected_items = []
    total = 0
    total_units = 0

    for item_id, qty in quantities.items():
        if item_id not in MENU_LOOKUP:
            continue
        if not isinstance(qty, int) or qty < 0:
            return jsonify({"ok": False, "message": "Quantities must be non-negative integers."}), 400
        if qty == 0:
            continue

        item = MENU_LOOKUP[item_id]
        line_total = int(item["price"]) * qty
        selected_items.append(
            {
                "id": item_id,
                "name": item["name"],
                "qty": qty,
                "unitPrice": item["price"],
                "lineTotal": line_total,
            }
        )
        total += line_total
        total_units += qty

    if not name or not pickup_date or total_units == 0:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "Please provide your name, pickup date, and at least one pastry item.",
                }
            ),
            400,
        )

    return jsonify(
        {
            "ok": True,
            "message": f"Thanks {name}! Your request is ready for {pickup_date}.",
            "order": {
                "name": name,
                "pickupDate": pickup_date,
                "size": size,
                "notes": notes,
                "items": selected_items,
                "total": total,
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
