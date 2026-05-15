# 极简菜谱日历（Web 应用版）

在不修改 `docs/` 的前提下，基于菜谱做了一个可在网页上操作的极简程序。

## 功能

1. 录入每天早/中/晚吃了哪道菜（可留空）。
2. 菜谱日历：页面按日期展示三餐记录。
3. 菜品统计：按每周、每月统计某道菜被选择次数。

## 启动

```bash
pip install flask
python3 minimalist_app/app.py
```

浏览器访问：`http://127.0.0.1:8000`

## 数据文件

- `minimalist_app/meal_records.json`
