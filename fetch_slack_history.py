from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os
from datetime import datetime
import csv

#import .env file
load_dotenv()

#Bot token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

#Channel ID
CHANNEL_ID = os.getenv("CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

#main function
def fetch_channel_messages_with_threads(channel_id, limit=100):
    all_messages = []
    try:
        result = client.conversations_history(channel=channel_id, limit=limit)
        messages = result.get("messages", [])

        for msg in messages:
            ts = msg.get("ts")
            all_messages.append({
                "ts": ts,
                "user": msg.get("user"),
                "text": msg.get("text"),
                "is_thread": False,
                "parent_ts": None
            })

            # スレッドがある場合は取得
            if msg.get("thread_ts") and msg.get("reply_count", 0) > 0:
                replies = client.conversations_replies(channel=channel_id, ts=ts).get("messages", [])[1:]
                for reply in replies:
                    all_messages.append({
                        "ts": reply.get("ts"),
                        "user": reply.get("user"),
                        "text": reply.get("text"),
                        "is_thread": True,
                        "parent_ts": ts
                    })

        # ★ 時系列順に並べ替え（親＋返信すべて）
        all_messages = sorted(all_messages, key=lambda msg: float(msg["ts"]))

    except SlackApiError as e:
        print(f"Error fetching messages: {e.response['error']}")
    
    return all_messages

#export messages to csv
def save_messages_to_csv(messages, filename="chat_history.csv"):
    # utf-8-sigを使用することで、Excelでも文字化けせずに開ける
    # AIに読み込ませる際も問題なく動作します
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "User ID", "Message"])
        for msg in messages:
            ts = msg.get("ts", "")
            date_str = datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            user = msg.get("user","system/bot")
            text = msg.get("text","")
            writer.writerow([date_str, user, text])
#execute
messages = fetch_channel_messages_with_threads(CHANNEL_ID)
save_messages_to_csv(messages)
