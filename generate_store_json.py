import pandas as pd
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
import os
from dotenv import load_dotenv

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 環境変数読み込み
load_dotenv()

def connect_to_spreadsheet():
    """Google Spreadsheetに接続"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'idyllic-kit-451707-e2-2d3d4fa320cb.json')
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Google Spreadsheet接続エラー: {str(e)}")
        raise

def validate_store_data(store):
    """店舗データのバリデーション"""
    required_fields = ["店舗ID", "店舗名", "タイトル"]
    missing_fields = [field for field in required_fields if not store.get(field)]
    
    if missing_fields:
        raise ValueError(f"必須フィールドが不足しています: {', '.join(missing_fields)}")

    # 質問のバリデーション
    for i in range(1, 7):
        if not store.get(f"質問{i}"):
            logger.warning(f"質問{i}が設定されていません: {store['店舗名']}")

def process_questions(row):
    """質問データの処理"""
    questions = []
    for i in range(1, 7):
        label = row.get(f"質問{i}")
        if not label:
            continue
            
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
    return questions

def main():
    try:
        # Spreadsheet接続
        client = connect_to_spreadsheet()
        spreadsheet_key = os.getenv('SPREADSHEET_KEY', '1EkQQV9SZLiIA4VOXPpmaCBHODcecVnvL9NH4JZ12rck')
        sheet = client.open_by_key(spreadsheet_key).sheet1

        # データ取得
        df = pd.DataFrame(sheet.get_all_records())
        df = df.where(pd.notnull(df), None)

        # 店舗データ作成
        store_data = []
        for _, row in df.iterrows():
            try:
                validate_store_data(row)

    store = {
        "store_id": str(row["店舗ID"]),
        "store_name": row["店舗名"],
        "title": row["タイトル"] or f"{row['店舗名']}｜アンケート",
        "hero_image": row.get("画像URL"),
        "store_logo": row.get("投稿サイトロゴURL"),
        "google_img": row.get("GoogleロゴURL"),
        "google_link": row.get("Google投稿URL"),
        "store_link": row.get("投稿サイトURL"),
                    "questions": process_questions(row)
    }
    store_data.append(store)
                logger.info(f"✅ 店舗データ作成完了: {row['店舗名']}")
                
            except Exception as e:
                logger.error(f"❌ 店舗データ作成エラー ({row.get('店舗名', '不明')}): {str(e)}")
                continue

# JSON出力
with open("store.json", "w", encoding="utf-8") as f:
    json.dump(store_data, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ store.json を生成しました。全{len(store_data)}件の店舗データ")

    except Exception as e:
        logger.error(f"❌ 致命的なエラー: {str(e)}")
        raise

if __name__ == "__main__":
    main()
