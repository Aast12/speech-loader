import internetarchive
from internetarchive import Item, File
from datetime import datetime
from query import IASearchQueryBuilder
from typing import Tuple, Generator, Callable
from pydub import AudioSegment
from dataclasses import dataclass
import logging

@dataclass
class IACrawlerConfig:
    item_limit: int
    size_limit: int
    download_path: str


class IACrawler:
    query_string: str
    bounds: IACrawlerConfig

    def __init__(
        self, search_query: IASearchQueryBuilder, config: IACrawlerConfig
    ) -> None:
        self.query_string = search_query.build_query()
        self.bounds = config

    def __extract_audio_metadata(self, item: Item, file: File) -> Tuple[str, dict]:
        """
        Returns audio file metadata fields from an internet archive file entry.
        """
        file_path = f"{self.bounds.download_path}/{file.name}"
        item_source_date = None
        try:
            item_source_date = datetime.strptime(item.metadata["date"], "%y-%m-%d")
        except ValueError:
            logging.info(f"Unable to parse source date for item_id={item.metadata["identifier"]}")
            pass

        file_meta = {
            "internet_archive_item_id": item.metadata["identifier"],
            "internet_archive_file_id": file.identifier,
            "file_path": file_path,
            "file_size": int(file.size),
            "source_date": item_source_date,
        }

        return (file_path, file_meta)

    def __extract_audio_features(self, file_path: str) -> dict:
        """Returns core features from an audio file."""
        audio = AudioSegment.from_file(file_path, format="mp3")

        max_dbfs = audio.max_dBFS
        bdfs = audio.dBFS
        rms = audio.rms
        duration = audio.duration_seconds

        audio_features = {
            "max_dbfs": max_dbfs,
            "dbfs": bdfs,
            "rms": rms,
            "duration": duration,
        }

        return audio_features

    def search(
        self, should_download: Callable[[str, dict], bool] = None
    ) -> Generator[dict, None, None]:
        if should_download is None:
            should_download = lambda _: True

        results = internetarchive.search_items(
            self.query_string, sorts=["downloads desc"]
        )
        logging.info("Starting audio search")
        for index, item in enumerate(results.iter_as_items()):
            if index > self.bounds.item_limit:
                break

            item_files = item.get_files(formats=["MP3", "VBR MP3"])
            for file in item_files:
                if file.size > self.bounds.size_limit:
                    continue

                file_path, file_meta = self.__extract_audio_metadata(item, file)

                if not should_download(file_path, file_meta):
                    logging.info(f"file_id={file_meta["internet_archive_file_id"]} skipped")
                    continue

                with open(file_path, "xb") as fileobj:
                    file.download(fileobj=fileobj)

                audio_features = self.__extract_audio_features(file_path)

                yield {**file_meta, **audio_features}
