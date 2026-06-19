from googleapiclient.discovery import build
from auth import get_credentials
import os

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "1PxEh2tewlrDwf2yPgpAOAlh3cIOPL1GuIROmP4Ad5pM")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# 記録一覧シートの列（既存シートに合わせた順序）
COLUMNS = [
    "No.", "記録日", "茶葉名", "産地", "茶類", "年份",
    "水温(℃)", "評価", "また飲みたい", "メモ",
    "写真①URL", "写真②URL",
    # 詳細項目
    "場所", "天気", "茶号/品番", "海抜", "茶山環境", "茶樹年齢", "樹形", "土質",
    "茶壺材質", "水質", "茶葉量(g)", "注湯量(ml)", "出汤速度", "冲泡次数(煎)", "焼水方式",
    "水色", "透明度", "茶葉形態",
    "香りの種類", "香りの強さ", "純粋度", "持続時間",
    "口腔濃度", "前調", "中調", "後調", "水含香", "水含香種類",
    "回甘", "回甘持続", "生津", "生津持続",
    "喉韻", "喉韻の強さ", "身体反応", "推薦度",
]

# 行1=タイトル、行2=ヘッダー、行3以降=データ
HEADER_ROW = 2
DATA_START_ROW = 3


def _service():
    return build("sheets", "v4", credentials=get_credentials(SCOPES))


def _ensure_headers(service):
    """ヘッダー行が存在しない列は追記する"""
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"記録一覧!{HEADER_ROW}:{HEADER_ROW}"
    ).execute()
    existing = result.get("values", [[]])[0] if result.get("values") else []

    if len(existing) < len(COLUMNS):
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"記録一覧!A{HEADER_ROW}",
            valueInputOption="USER_ENTERED",
            body={"values": [COLUMNS]},
        ).execute()


def get_next_no(service):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"記録一覧!A{DATA_START_ROW}:A"
    ).execute()
    rows = result.get("values", [])
    return len(rows) + 1


def append_record(record: dict, photo_urls: list):
    service = _service()
    _ensure_headers(service)
    no = get_next_no(service)

    row = {col: "" for col in COLUMNS}
    row["No."] = f"{no:04d}"
    for k, v in record.items():
        if k in row:
            row[k] = v
    row["写真①URL"] = photo_urls[0] if len(photo_urls) > 0 else ""
    row["写真②URL"] = photo_urls[1] if len(photo_urls) > 1 else ""

    values = [[row[col] for col in COLUMNS]]
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"記録一覧!A{DATA_START_ROW}",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()
    return no


def get_all_records():
    service = _service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"記録一覧!A{HEADER_ROW}:AZ"
    ).execute()
    values = result.get("values", [])
    if len(values) < 2:
        return []
    headers = values[0]
    records = []
    for row in values[1:]:
        rec = {h: (row[i] if i < len(row) else "") for i, h in enumerate(headers)}
        records.append(rec)
    return records
