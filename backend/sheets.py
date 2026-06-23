from googleapiclient.discovery import build
from auth import get_credentials
import os

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "1PxEh2tewlrDwf2yPgpAOAlh3cIOPL1GuIROmP4Ad5pM")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

TEMPLATE_SHEET_ID = 877446008  # No.0001 シートのID

COLUMNS = [
    "No.", "記録日", "茶葉名", "産地", "茶類", "年份",
    "水温(℃)", "評価", "また飲みたい", "メモ",
    "写真①URL", "写真②URL", "写真③URL", "写真④URL",
    "場所", "天気", "茶号/品番", "海抜", "茶山環境", "茶樹年齢", "樹形", "土質",
    # 茶器情報
    "茶器名", "窯元/作家", "茶器産地", "茶器年代", "容量(ml)",
    "茶壺材質", "水質", "茶葉量(g)", "注湯量(ml)", "出汤速度", "冲泡次数(煎)", "焼水方式",
    "水色", "透明度", "茶葉形態",
    "香りの種類", "香りの強さ", "純粋度", "持続時間",
    "口腔濃度", "前調", "中調", "後調", "水含香", "水含香種類",
    "回甘", "回甘持続", "生津", "生津持続",
    "喉韻", "喉韻の強さ", "身体反応", "推薦度",
]

HEADER_ROW = 2
DATA_START_ROW = 3


def _service():
    return build("sheets", "v4", credentials=get_credentials(SCOPES))


def _ensure_headers(service):
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


def _fmt_rating(val):
    try:
        n = int(val)
    except (ValueError, TypeError):
        return ""
    return "★" * n + "☆" * (5 - n) + f"　（{n}）"


def create_record_tab(service, no: int, record: dict, photo_urls: list):
    """No.0001テンプレートを複製してNo.XXXXタブを作成しデータを入力する"""
    no_str = f"{no:04d}"
    sheet_title = f"No.{no_str}"

    # テンプレートシートを複製（新シートIDを取得）
    dup_resp = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [{"duplicateSheet": {
            "sourceSheetId": TEMPLATE_SHEET_ID,
            "insertSheetIndex": 999,
            "newSheetName": sheet_title,
        }}]}
    ).execute()
    new_sheet_id = dup_resp["replies"][0]["duplicateSheet"]["properties"]["sheetId"]

    # テンプレートの例示データをクリア（ラベル行は残す）
    clear_ranges = [
        f"{sheet_title}!G3",
        f"{sheet_title}!C6:G6",
        f"{sheet_title}!C7:G7",
        f"{sheet_title}!C8:I8",
        f"{sheet_title}!C9:I9",
        f"{sheet_title}!D12:G12",
        f"{sheet_title}!D13:G13",
        f"{sheet_title}!C16:I16",
        f"{sheet_title}!C17:I17",
        f"{sheet_title}!D18:G18",
        f"{sheet_title}!D21:G21",
        f"{sheet_title}!D22:I22",
        f"{sheet_title}!D25:I25",
        f"{sheet_title}!D26:I26",
        f"{sheet_title}!D27:I27",
        f"{sheet_title}!D30:I30",
        f"{sheet_title}!D31:I31",
        f"{sheet_title}!D32:I32",
        f"{sheet_title}!D33:I33",
        f"{sheet_title}!D34:I34",
        f"{sheet_title}!D37:I37",
        f"{sheet_title}!D38:I38",
        f"{sheet_title}!C41:I41",
        f"{sheet_title}!D42:G42",
        f"{sheet_title}!B46:I50",
    ]
    service.spreadsheets().values().batchClear(
        spreadsheetId=SPREADSHEET_ID,
        body={"ranges": clear_ranges}
    ).execute()

    def v(key, default=""):
        return str(record.get(key) or default)

    def with_unit(key, unit):
        val = v(key)
        return f"{val} {unit}" if val else ""

    # セルマッピング: (A1表記, 値)
    cell_data = [
        (f"{sheet_title}!G3",  f"No.  {no_str}"),
        (f"{sheet_title}!C6",  v("記録日")),
        (f"{sheet_title}!E6",  v("天気")),
        (f"{sheet_title}!G6",  v("場所")),
        (f"{sheet_title}!C7",  v("茶葉名")),
        (f"{sheet_title}!G7",  v("茶号/品番")),
        (f"{sheet_title}!C8",  v("茶類")),
        (f"{sheet_title}!E8",  v("産地")),
        (f"{sheet_title}!H8",  v("海抜")),
        (f"{sheet_title}!C9",  v("年份")),
        (f"{sheet_title}!E9",  v("茶山環境")),
        (f"{sheet_title}!H9",  v("茶樹年齢")),
        (f"{sheet_title}!D12", v("樹形")),
        (f"{sheet_title}!D13", v("土質")),
        (f"{sheet_title}!C16", v("茶壺材質")),
        (f"{sheet_title}!F16", v("水質")),
        (f"{sheet_title}!I16", with_unit("水温(℃)", "℃")),
        (f"{sheet_title}!C17", with_unit("茶葉量(g)", "g")),
        (f"{sheet_title}!E17", with_unit("注湯量(ml)", "ml")),
        (f"{sheet_title}!G17", v("出汤速度")),
        (f"{sheet_title}!I17", with_unit("冲泡次数(煎)", "煎")),
        (f"{sheet_title}!D18", v("焼水方式")),
        (f"{sheet_title}!D21", v("水色")),
        (f"{sheet_title}!D22", v("透明度")),
        (f"{sheet_title}!G22", v("茶葉形態")),
        (f"{sheet_title}!D25", v("香りの種類")),
        (f"{sheet_title}!D26", v("香りの強さ")),
        (f"{sheet_title}!H26", v("純粋度")),
        (f"{sheet_title}!D27", v("持続時間")),
        (f"{sheet_title}!D30", v("口腔濃度")),
        (f"{sheet_title}!H30", v("水含香")),
        (f"{sheet_title}!D31", v("前調")),
        (f"{sheet_title}!H31", v("中調")),
        (f"{sheet_title}!D32", v("後調")),
        (f"{sheet_title}!H32", v("水含香種類")),
        (f"{sheet_title}!D33", v("回甘")),
        (f"{sheet_title}!H33", v("回甘持続")),
        (f"{sheet_title}!D34", v("生津")),
        (f"{sheet_title}!H34", v("生津持続")),
        (f"{sheet_title}!D37", v("喉韻")),
        (f"{sheet_title}!H37", v("喉韻の強さ")),
        (f"{sheet_title}!D38", v("身体反応")),
        (f"{sheet_title}!C41", _fmt_rating(v("評価"))),
        (f"{sheet_title}!G41", v("また飲みたい")),
        (f"{sheet_title}!D42", v("推薦度")),
        (f"{sheet_title}!B46", v("メモ")),
        # 写真4枚：行51-56を4分割（B51上半,B54下半,F51上半,F54下半）
        (f"{sheet_title}!B51",
         f'=IMAGE("{photo_urls[2]}", 1)' if len(photo_urls) > 2 and photo_urls[2] else "茶 器"),
        (f"{sheet_title}!B54",
         f'=IMAGE("{photo_urls[0]}", 1)' if len(photo_urls) > 0 and photo_urls[0] else "茶 葉 · 外 觀"),
        (f"{sheet_title}!F51",
         f'=IMAGE("{photo_urls[1]}", 1)' if len(photo_urls) > 1 and photo_urls[1] else "水 色 · 茶 湯"),
        (f"{sheet_title}!F54",
         f'=IMAGE("{photo_urls[3]}", 1)' if len(photo_urls) > 3 and photo_urls[3] else "設 え"),
    ]

    # まとめて一括更新
    data = [{"range": rng, "values": [[val]]} for rng, val in cell_data if val]
    if data:
        service.spreadsheets().values().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": data}
        ).execute()

    # 写真エリア（行51-56）を4分割して4枚均等表示
    # テンプレートの正確なマージ範囲: 左=B:E(col1-5), 右=F:I(col5-9)
    try:
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": [
                # 既存マージ解除（左右両エリア）
                {"unmergeCells": {"range": {"sheetId": new_sheet_id,
                    "startRowIndex": 50, "endRowIndex": 56,
                    "startColumnIndex": 1, "endColumnIndex": 5}}},  # B:E
                {"unmergeCells": {"range": {"sheetId": new_sheet_id,
                    "startRowIndex": 50, "endRowIndex": 56,
                    "startColumnIndex": 5, "endColumnIndex": 9}}},  # F:I
                # 左上（B51:E53）：茶器
                {"mergeCells": {"range": {"sheetId": new_sheet_id,
                    "startRowIndex": 50, "endRowIndex": 53,
                    "startColumnIndex": 1, "endColumnIndex": 5},
                    "mergeType": "MERGE_ALL"}},
                # 左下（B54:E56）：茶葉
                {"mergeCells": {"range": {"sheetId": new_sheet_id,
                    "startRowIndex": 53, "endRowIndex": 56,
                    "startColumnIndex": 1, "endColumnIndex": 5},
                    "mergeType": "MERGE_ALL"}},
                # 右上（F51:I53）：水色・茶湯
                {"mergeCells": {"range": {"sheetId": new_sheet_id,
                    "startRowIndex": 50, "endRowIndex": 53,
                    "startColumnIndex": 5, "endColumnIndex": 9},
                    "mergeType": "MERGE_ALL"}},
                # 右下（F54:I56）：設え
                {"mergeCells": {"range": {"sheetId": new_sheet_id,
                    "startRowIndex": 53, "endRowIndex": 56,
                    "startColumnIndex": 5, "endColumnIndex": 9},
                    "mergeType": "MERGE_ALL"}},
            ]}
        ).execute()
    except Exception as e:
        print(f"photo merge failed (non-fatal): {e}")


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
    row["写真③URL"] = photo_urls[2] if len(photo_urls) > 2 else ""
    row["写真④URL"] = photo_urls[3] if len(photo_urls) > 3 else ""

    values = [[row[col] for col in COLUMNS]]
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"記録一覧!A{DATA_START_ROW}",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()

    # テンプレートからタブを自動生成
    try:
        create_record_tab(service, no, record, photo_urls)
    except Exception as e:
        print(f"create_record_tab failed (non-fatal): {e}")

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
