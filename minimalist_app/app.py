#!/usr/bin/env python3
"""极简菜谱日历程序（命令行版）。

功能：
1. 记录某日期早餐/午餐/晚餐吃了哪道菜（未选择保持为空）。
2. 查看日历式列表（按日期展示三餐）。
3. 按菜品统计每周、每月被选择次数。
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List

DATA_FILE = Path(__file__).with_name("meal_records.json")

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


@dataclass
class Record:
    breakfast: str = ""
    lunch: str = ""
    dinner: str = ""

    def as_dict(self) -> Dict[str, str]:
        return {"早餐": self.breakfast, "午餐": self.lunch, "晚餐": self.dinner}


def load_data() -> Dict[str, Dict[str, str]]:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {}


def save_data(data: Dict[str, Dict[str, str]]) -> None:
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def choose_date() -> str:
    raw = input("请输入日期（YYYY-MM-DD）: ").strip()
    datetime.strptime(raw, "%Y-%m-%d")
    return raw


def choose_dish(meal_type: str) -> str:
    print(f"\n请选择{meal_type}（输入编号，直接回车表示留空）")
    for idx, dish in enumerate(DISHES[meal_type], start=1):
        print(f"{idx}. {dish}")

    choice = input("你的选择: ").strip()
    if not choice:
        return ""
    index = int(choice) - 1
    if index < 0 or index >= len(DISHES[meal_type]):
        raise ValueError("菜品编号无效")
    return DISHES[meal_type][index]


def add_or_update_record(data: Dict[str, Dict[str, str]]) -> None:
    d = choose_date()
    old = data.get(d, {"早餐": "", "午餐": "", "晚餐": ""})
    print(f"\n当前记录：早餐={old['早餐'] or '空'} | 午餐={old['午餐'] or '空'} | 晚餐={old['晚餐'] or '空'}")

    breakfast = choose_dish("早餐")
    lunch = choose_dish("午餐")
    dinner = choose_dish("晚餐")

    data[d] = Record(breakfast, lunch, dinner).as_dict()
    save_data(data)
    print("\n✅ 已保存。")


def show_calendar(data: Dict[str, Dict[str, str]]) -> None:
    if not data:
        print("\n暂无记录。")
        return

    print("\n=== 菜谱日历 ===")
    for d in sorted(data.keys()):
        row = data[d]
        print(
            f"{d} | 早餐: {row.get('早餐') or '空'} | "
            f"午餐: {row.get('午餐') or '空'} | 晚餐: {row.get('晚餐') or '空'}"
        )


def week_key(d: date) -> str:
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def stats_by_dish(data: Dict[str, Dict[str, str]]) -> None:
    period = input("统计周期（week/month）: ").strip().lower()
    if period not in {"week", "month"}:
        raise ValueError("仅支持 week 或 month")

    counter = Counter()
    for ds, row in data.items():
        d = datetime.strptime(ds, "%Y-%m-%d").date()
        key = week_key(d) if period == "week" else d.strftime("%Y-%m")
        for meal_name in ("早餐", "午餐", "晚餐"):
            dish = row.get(meal_name, "")
            if dish:
                counter[(key, dish)] += 1

    if not counter:
        print("\n暂无可统计数据。")
        return

    print(f"\n=== 按菜品{('每周' if period == 'week' else '每月')}统计 ===")
    for (key, dish), count in sorted(counter.items(), key=lambda x: (x[0][0], -x[1], x[0][1])):
        print(f"{key} | {dish} | {count} 次")


def main() -> None:
    data = load_data()
    actions = {
        "1": ("新增/修改某日三餐", add_or_update_record),
        "2": ("查看菜谱日历", show_calendar),
        "3": ("按菜品统计（每周/每月）", stats_by_dish),
        "0": ("退出", None),
    }

    while True:
        print("\n====== 极简菜谱日历 ======")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        cmd = input("请选择功能: ").strip()

        if cmd == "0":
            print("再见！")
            return

        action = actions.get(cmd)
        if not action:
            print("无效选项，请重试。")
            continue

        try:
            action[1](data)
        except Exception as exc:
            print(f"⚠️ 操作失败：{exc}")


if __name__ == "__main__":
    main()
