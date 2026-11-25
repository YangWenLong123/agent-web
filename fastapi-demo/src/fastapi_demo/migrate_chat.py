"""用法：PYTHONPATH=src .venv/bin/python -m fastapi_demo.migrate_chat。"""
import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from fastapi_demo.mysql_conversations import MySQLConversationRepository, MySQLSettings


def main():
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")
    parser = argparse.ArgumentParser(description="将 SQLite 历史问答复制到配置的 MySQL，保留源数据库。")
    parser.add_argument("--source", type=Path, default=root / "data" / "chat.sqlite3")
    args = parser.parse_args()
    repository = MySQLConversationRepository(MySQLSettings.from_env(), recover_unfinished=False)
    try:
        print(json.dumps(repository.migrate_from_sqlite(args.source), ensure_ascii=False))
    finally:
        repository.close()


if __name__ == "__main__":
    main()
