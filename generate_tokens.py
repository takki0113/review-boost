import json
import secrets
import gspread
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from gspread.utils import rowcol_to_a1

# 🔐 Google認証
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials/idyllic-kit-451707-e2-07069bcdc17f.json', scope)
client = gspread.authorize(creds)

# 📊 スプレッドシート読み込み
spreadsheet_key = '1EkQQV9SZLiIA4VOXPpmaCBHODcecVnvL9NH4JZ12rck'
sheet = client.open_by_key(spreadsheet_key).sheet1

# 📥 データ取得 & DataFrame化
df = pd.DataFrame(sheet.get_all_records())

# 🧼 NaNなどJSON非対応値をクリーンに
def clean_cell(val):
    if isinstance(val, float) and not np.isfinite(val):
        return ""
    if pd.isna(val):
        return ""
    return val

df = df.applymap(clean_cell)

# 🔐 トークン生成 & マップ保持
token_map = {}
for i, row in df.iterrows():
    store_id = str(row.get("店舗ID", "")).strip()
    store_name = str(row.get("店舗名", "")).strip()

    if not store_id or not store_name:
        continue

    token = str(row.get("トークン", "")).strip()
    if not token:
        token = secrets.token_urlsafe(12)
        df.at[i, 'トークン'] = token

    token_map[token] = store_id

# 🌐 アクセスURL生成
BASE_URL = "https://review-ai-api-2.onrender.com"
df["アクセスURL"] = df["トークン"].apply(lambda t: f"{BASE_URL}/?t={t}" if t else "")

# 💾 tokens.json に保存
with open("tokens.json", "w", encoding="utf-8") as f:
    json.dump(token_map, f, ensure_ascii=False, indent=2)

# ✅ 列インデックス特定（1始まり）
token_col_index = df.columns.get_loc("トークン") + 1
url_col_index = df.columns.get_loc("アクセスURL") + 1
start_row = 2  # 1行目はヘッダー

# 📤 トークン列を安全更新
for i, token in enumerate(df["トークン"].tolist()):
    cell = rowcol_to_a1(start_row + i, token_col_index)
    sheet.update_acell(cell, token)

# 📤 アクセスURL列を安全更新
for i, url in enumerate(df["アクセスURL"].tolist()):
    cell = rowcol_to_a1(start_row + i, url_col_index)
    sheet.update_acell(cell, url)

print("✅ トークン + URL列を非破壊で安全反映完了 🎯")
