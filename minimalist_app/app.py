#!/usr/bin/env python3
"""极简菜谱日历程序（Web 版）。"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

from flask import Flask, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "meal_records.json"
TEMPLATES_DIR = BASE_DIR / "templates"

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))

DISHES: Dict[str, List[str]] = {
    "早餐": [
        "🥣 燕麦牛奶早餐",
        "🌽 玉米鸡蛋早餐",
        "🍠 红薯酸奶早餐",
        "🥛 山药豆浆早餐",
        "🍓 燕麦酸奶水果碗",
        "☕ 黑咖啡简易早餐",
        "🍜 鸡蛋蔬菜荞麦面",
        "🎃 小米南瓜粥早餐",
    ],
    "午餐": [
        "🍅 番茄鸡胸肉杂粮饭",
        "🍤 虾仁豆腐盖饭",
        "🍚 肉末豆腐 + 青菜 + 糙米饭",
        "🍗 鸡腿肉 + 冬瓜汤 + 糙米饭",
        "🐟 清蒸鱼 + 西兰花 + 小米饭",
    ],
    "晚餐": [
        "🍗 黑胡椒鸡胸肉 + 西兰花 + 玉米",
        "🍅 番茄鸡蛋荞麦面 + 生菜",
        "🍤 虾仁豆腐 + 黄瓜 + 糙米饭",
        "🐟 香煎巴沙鱼 + 红薯 + 菠菜",
        "🍲 菌菇鸡蛋汤 + 凉拌蔬菜 + 玉米/红薯",
        "🍚 肉末豆腐 + 青菜 + 糙米饭",
        "🍗 鸡腿肉 + 冬瓜汤 + 糙米饭",
        "🐠 清蒸鱼 + 西兰花 + 小米饭",
    ],
}


def load_data() -> Dict[str, Dict[str, str]]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


def save_data(data: Dict[str, Dict[str, str]]) -> None:
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def week_key(d: date) -> str:
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def build_stats(data: Dict[str, Dict[str, str]], period: str):
    counter = Counter()
    for ds, row in data.items():
        d = datetime.strptime(ds, "%Y-%m-%d").date()
        key = week_key(d) if period == "week" else d.strftime("%Y-%m")
        for meal_name in ("早餐", "午餐", "晚餐"):
            dish = row.get(meal_name, "")
            if dish:
                counter[(key, dish)] += 1

    return [
        {"period": key, "dish": dish, "count": count}
        for (key, dish), count in sorted(counter.items(), key=lambda x: (x[0][0], -x[1], x[0][1]))
    ]


@app.get("/")
def home():
    data = load_data()
    selected_date = request.args.get("date", "")
    record = data.get(selected_date, {"早餐": "", "午餐": "", "晚餐": ""}) if selected_date else None

    calendar_rows = []
    for d in sorted(data.keys()):
        row = data[d]
        calendar_rows.append(
            {
                "date": d,
                "早餐": row.get("早餐", "") or "空",
                "午餐": row.get("午餐", "") or "空",
                "晚餐": row.get("晚餐", "") or "空",
            }
        )

    return render_template(
        "index.html",
        dishes=DISHES,
        selected_date=selected_date,
        record=record,
        calendar_rows=calendar_rows,
        default_date=datetime.now().strftime("%Y-%m-%d"),
    )


@app.post("/save")
def save_record():
    d = request.form.get("date", "").strip()
    datetime.strptime(d, "%Y-%m-%d")

    data = load_data()
    data[d] = {
        "早餐": request.form.get("早餐", "").strip(),
        "午餐": request.form.get("午餐", "").strip(),
        "晚餐": request.form.get("晚餐", "").strip(),
    }
    save_data(data)
    return redirect(url_for("home", date=d))


@app.get("/stats")
def stats():
    period = request.args.get("period", "week")
    if period not in {"week", "month"}:
        period = "week"

    rows = build_stats(load_data(), period)
    return render_template("stats.html", rows=rows, period=period)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
