import internetarchivefrom typing import Optional, List
import pprint
from query import IACollection, IASearchQueryBuilder
from datetime import datetime, timedelta

# Runtime limit for a crawled audio file to be processed
RUNTIME_LIMIT = timedelta(minutes=15)


def search():
    q = IASearchQueryBuilder()\
        .set_collection(IACollection.PRESIDENTIAL_RECORDINGS)\
        .set_language(["English", "eng"])\
        .set_media_type("audio")

    query_str = q.build_query()
    print(query_str)
    results = internetarchive.search_items(query_str, sorts=["downloads desc"])

    limit = 0
    for item in results.iter_as_items():
        pprint.pprint(item.metadata)
        limit += 1
        if limit > 10:
            break


search()
