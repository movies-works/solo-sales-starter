"""次案の試作品：無料・登録不要のフォロー期限チェッカー（v2）。

目的：販売・決済・口座を一切使わず、無料公開だけで実績と見込み客を積む。
前夜の followup.py はサンプルCSV専用だったため、任意のCSVを受け取れる形に拡張した。
使い方：
  python3 followup_free.py --csv customers.csv --date 2026-10-29
  python3 followup_free.py --csv customers.csv --date 2026-10-29 --out report.md
CSVの列名：顧客名, 次アクション, 次アクション日（YYYY-MM-DD）
出力：期限切れ／今日／明日／今週（2〜7日後）／それ以降 の件数と一覧。
個人情報は外部に送らない。ファイル読み込みと画面出力のみ。
"""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path


def classify(rows, today):
    groups = {"期限切れ": [], "今日": [], "明日": [], "今週（2〜7日後）": [], "それ以降": []}
    for row in rows:
        due = date.fromisoformat(row["次アクション日"].strip())
        delta = (due - today).days
        label = f"{row['顧客名']} / {row['次アクション']} / {row['次アクション日']}"
        if delta < 0:
            groups["期限切れ"].append(label)
        elif delta == 0:
            groups["今日"].append(label)
        elif delta == 1:
            groups["明日"].append(label)
        elif 2 <= delta <= 7:
            groups["今週（2〜7日後）"].append(label)
        else:
            groups["それ以降"].append(label)
    return groups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    today = date.fromisoformat(args.date)
    with open(args.csv, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("入力CSVにデータ行がありません。")
        return 1
    for col in ("顧客名", "次アクション", "次アクション日"):
        if col not in rows[0]:
            print(f"列名が不足しています。必要: 顧客名, 次アクション, 次アクション日 / 実際: {list(rows[0].keys())}")
            return 1
    groups = classify(rows, today)
    lines = [f"# フォロー期限チェック（基準日 {today.isoformat()}）", ""]
    total_action = 0
    for name, items in groups.items():
        lines.append(f"## {name}: {len(items)}件")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
        if name != "それ以降":
            total_action += len(items)
    lines.append(f"直近の対応対象（期限切れ〜今週）: {total_action}件 / 全 {len(rows)}件")
    text = "\n".join(lines)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"保存: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
