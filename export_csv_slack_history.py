from datetime import datetime

#export csv slack history
import csv 

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
