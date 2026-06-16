from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

COLUMNS = [
    "No.", "記録日", "茶葉名", "産地", "茶類", "茶号/品番", "年份", "場所", "天気",
    "海抜", "茶山環境", "茶樹年齢", "樹形", "土質",
    "茶壺材質", "水質", "水温(℃)", "茶葉量(g)", "注湯量(ml)", "出汤速度", "冲泡次数(煎)", "焼水方式",
    "水色", "透明度", "茶葉形態",
    "香りの種類", "香りの強さ", "純粋度", "持続時間",
    "口腔濃度", "前調", "中調", "後調", "水含香", "水含香種類", "回甘", "回甘持続", "生津", "生津持続",
    "喉韻", "喉韻の強さ", "身体反応",
    "評価", "また飲みたい", "推薦度",
    "写真①URL", "写真②URL",
    "メモ",
]


def _service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds)


def get_next_no(service):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="記録一覧!A:A"
    ).execute()
    values = result.get("values", [])
    return len(values)  # row count including header = next No.


def append_record(record: dict, photo_urls: list[str]):
    service = _service()
    no = get_next_no(service)

    row = {col: "" for col in COLUMNS}
    row["No."] = f"{no:04d}"
    row.update(record)
    row["写真①URL"] = photo_urls[0] if len(photo_urls) > 0 else ""
    row["写真②URL"] = photo_urls[1] if len(photo_urls) > 1 else ""

    values = [[row[col] for col in COLUMNS]]
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="記録一覧!A1",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()
    return no


def get_all_records():
    service = _service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="記録一覧!A1:AV"
    ).execute()
    values = result.get("values", [])
    if len(values) < 2:
        return []
    headers = values[0]
    records = []
    for row in values[1:]:
        rec = {}
        for i, h in enumerate(headers):
            rec[h] = row[i] if i < len(row) else ""
        records.append(rec)
    return records
