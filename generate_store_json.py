import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# スプレッドシート認証
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/idyllic-kit-451707-e2-f4b8c26a1c26.json', scope)
client = gspread.authorize(creds)

# 対象のスプレッドシートとシートを指定
spreadsheet_key = '1EkQQV9SZLiIA4VOXPpmaCBHODcecVnvL9NH4JZ12rck'
sheet = client.open_by_key(spreadsheet_key).sheet1

# シートのデータをDataFrameに変換
df = pd.DataFrame(sheet.get_all_records())

# NaN を None に置換
df = df.where(pd.notnull(df), None)

# 店舗データ作成
store_data = []

for _, row in df.iterrows():
    # ✅ 店舗IDか店舗名が空ならスキップ
    if not row.get("店舗ID") or not row.get("店舗名"):
        continue

    questions = []
    for i in range(1, 7):
        label = row.get(f"質問{i}")
        qtype = "textarea" if i == 6 else "select"
        options_raw = row.get(f"質問{i} 回答")
        options = [opt.strip() for opt in options_raw.split(",")] if options_raw else []

        question = {
            "id": f"q{i}",
            "label": label,
            "type": qtype
        }
        if qtype == "select":
            question["options"] = options
        else:
            question["placeholder"] = "例：スタッフさんがとても親切でした。"
        questions.append(question)

    print("🎯 店舗:", row["店舗名"])
    print("🖼️ hero_image:", row.get("画像URL"))
    print("🖼️ store_logo:", row.get("投稿サイトロゴURL"))

    store = {
        "store_id": str(row["店舗ID"]),
        "store_name": row["店舗名"],
        "title": row["タイトル"] or f"{row['店舗名']}｜アンケート",
        "hero_image": row.get("画像URL"),
        "store_logo": row.get("投稿サイトロゴURL"),
        "google_link": row.get("Google投稿URL"),
        "google_img": row.get("Google画像URL"),  # ← これを追加
        "store_link": row.get("投稿サイトURL"),
        "questions": questions
    }
    store_data.append(store)

# JSON 出力
with open("store.json", "w", encoding="utf-8") as f:
    json.dump(store_data, f, ensure_ascii=False, indent=2)

print("✅ store.json を生成しました。")
