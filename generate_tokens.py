import json
import secrets
import os

# 読み込み元のstore.json
with open("store.json", "r", encoding="utf-8") as f:
    stores = json.load(f)

# トークンを自動生成してマッピング
token_map = {}

for store in stores:
    store_id = store.get("store_id")
    if not store_id:
        continue

    # 16文字のURLセーフなトークン生成
    token = secrets.token_urlsafe(12)
    token_map[token] = store_id
    print(f"🔗 トークン生成: {token} → 店舗ID: {store_id}")

# 保存先
with open("tokens.json", "w", encoding="utf-8") as f:
    json.dump(token_map, f, ensure_ascii=False, indent=2)

print("✅ tokens.json を生成しました。トークン数:", len(token_map))
