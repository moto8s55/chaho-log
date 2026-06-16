"""
サービスアカウント認証のヘルパー。
環境変数 SERVICE_ACCOUNT_JSON（JSON文字列）か
SERVICE_ACCOUNT_FILE（ファイルパス）どちらでも動く。
"""
import os
import json
from google.oauth2 import service_account


def get_credentials(scopes: list[str]):
    json_str = os.environ.get("SERVICE_ACCOUNT_JSON")
    if json_str:
        info = json.loads(json_str)
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)

    filepath = os.environ.get("SERVICE_ACCOUNT_FILE", "service_account.json")
    return service_account.Credentials.from_service_account_file(filepath, scopes=scopes)
