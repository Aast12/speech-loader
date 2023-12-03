
import internetarchive
from internetarchive import Item
from query import IASearchQueryBuilder, IACollection
from datetime import datetime, timedelta
from models import Audio
import os
from pydub import AudioSegment
import pprint

# Runtime limit for a crawled audio file to be processed
RUNTIME_LIMIT = timedelta(minutes=15)
DOWNLOAD_PATH = "./files"
SIZE_LIMIT = 10_000_000

search_query = IASearchQueryBuilder()\
                .set_collection(IACollection.PRESIDENTIAL_RECORDINGS)\
                .set_language(["English", "eng"])\
                .set_media_type("audio")


def search(search_query: IASearchQueryBuilder):
    query_str = search_query.build_query()

    print(query_str)
    results = internetarchive.search_items(query_str, sorts=["downloads desc"])

    limit = 0
    for item in results.iter_as_items():

        item_files = item.get_files(formats=["MP3", "VBR MP3"])
        # pprint.pprint(item.metadata)
        for file in item_files:
            if file.size > SIZE_LIMIT:
                continue

            file_path = f"{DOWNLOAD_PATH}/{file.name}"

            if os.path.exists(file_path):
                print(file_path, "already exists")
                continue

            item_source_date = None
            try:
                item_source_date = datetime.strptime(item.metadata["date"], "%y-%m-%d")
            except ValueError:
                pass

            file_meta = {
                "internet_archive_item_id": item.metadata["identifier"],
                "internet_archive_file_id": file.identifier,
                "file_path": file_path,
                "file_size": int(file.size),
                "source_date": item_source_date
            }

            print(file_path, file.size)
            print(file.source)

            fileobj = open(file_path, "xb")
            file.download(fileobj=fileobj)
            fileobj.close()

            audio = AudioSegment.from_file(file_path, format='mp3')

            max_dbfs = audio.max_dBFS
            bdfs = audio.dBFS
            rms = audio.rms
            duration = audio.duration_seconds

            file_metrics = {
                'max_dbfs': max_dbfs,
                'dbfs': bdfs,
                'rms': rms,
                'duration': duration
            }

            audio_entry = Audio(**file_meta, **file_metrics)

            pprint.pprint(audio_entry)

            pprint.pprint(file_metrics)

            # file.download(file_path=DOWNLOAD_PATH, ignore_existing=True)
        limit += 1
        if limit > 20:
            break


search(search_query)
