from query import IASearchQueryBuilder, IACollection
from datetime import timedelta
from models import Audio
import os
from crawler import IACrawlerConfig, IACrawler
from db import SQLModel, engine, Audio
from sqlmodel import Session, select
import logging

logging.basicConfig(
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    level=logging.INFO,
)

# Search config/constraints
RUNTIME_LIMIT = timedelta(minutes=15)
DOWNLOAD_PATH = "./files"
SIZE_LIMIT = 10_000_000
ITEM_LIMIT = 100

search_query = (
    IASearchQueryBuilder()
    .set_collection(IACollection.PRESIDENTIAL_RECORDINGS)
    .set_language(["English", "eng"])
    .set_media_type("audio")
)

def should_download(file_path: str, file_meta: dict) -> bool:
    if os.path.exists(file_path):
        return False
    with Session(engine) as session:
        statement = (
            select(Audio)
            .where(
                Audio.internet_archive_file_id == file_meta["internet_archive_item_id"]
                and Audio.internet_archive_file_id
                == file_meta["internet_archive_item_id"]
            )
            .limit(1)
        )

        results = session.exec(statement)
        found_item = results.one_or_none()
        if found_item is not None:
            return False

    return True


if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
    session = Session(engine)

    crawler_conf = IACrawlerConfig(
        item_limit=ITEM_LIMIT, size_limit=SIZE_LIMIT, download_path=DOWNLOAD_PATH
    )
    crawler = IACrawler(search_query, crawler_conf)
    search_results = crawler.search(should_download)

    for audio_data in search_results:
        audio_entry = Audio(**audio_data)
        session.add(audio_entry)

    session.commit()
    session.close()
