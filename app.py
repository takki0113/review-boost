from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
import openai

# .env ファイルの読み込み
load_dotenv()

# OpenAI APIキー設定
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Flask アプリケーション初期化
app = Flask(__name__)
CORS(app)

# ディレクトリ設定
basedir = os.path.abspath(os.path.dirname(__file__))

# ✅ 店舗データ読み込み
with open(os.path.join(basedir, 'store.json'), 'r', encoding='utf-8') as f:
    stores = json.load(f)

# ✅ トークンとstore_idのマップ読み込み
# 例：{"abcdef123": "1", "ghijkl456": "2"}
with open(os.path.join(basedir, 'tokens.json'), 'r', encoding='utf-8') as f:
    token_map = json.load(f)

print("✅ store.json 読み込み成功。全件数:", len(stores))
print("✅ tokens.json 読み込み成功。登録トークン数:", len(token_map))

# ✅ ホームエントリーポイント：トークン方式
@app.route("/")
def home():
    token = request.args.get("t")
    if not token:
        return "❌ トークンが必要です。URLに ?t=xxx を付けてください。", 400

    store_id = token_map.get(token)
    if not store_id:
        return "❌ 無効なトークンです。", 404

    store_data = next((s for s in stores if s["store_id"] == store_id), None)
    if not store_data:
        return "❌ 店舗が見つかりませんでした。", 404

    print(f"🔓 トークン:{token} → store_id:{store_id}")
    return render_template("store.html", store=store_data)

# ❌ 廃止または開発者用（任意でコメントアウト可）
@app.route("/store/<store_id>")
def store_page(store_id):
    return "このURLは無効です。/?t=xxxx をご利用ください。", 403

# ✅ 口コミ生成API
@app.route("/api/generate", methods=["POST"])
def generate_review():
    data = request.get_json()
    prompt = data.get("prompt")
    print("📥 プロンプト受信:", prompt)

    if not prompt:
        return jsonify({"error": "プロンプトが空です"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは親しみやすく自然な日本語の口コミ文を作るアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        result = response.choices[0].message.content.strip()
        print("✅ 生成成功:", result)
        return jsonify({"result": result})
    except Exception as e:
        print("❌ エラー内容:", e)
        return jsonify({"error": str(e)}), 500

# アプリ起動
if __name__ == "__main__":
    app.run(debug=True)
