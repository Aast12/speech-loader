from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta


def parse_runtime(runtime_str: str) -> Optional[timedelta]:
    """
    Parse a runtime string from Internet Archive items into a time delta object.

    Returns None if runtime string is not valid.
    """
    formats = [
        "%H:%M:%S",
        "%M:%S"
    ]

    for format in formats:
        try:
            dt = datetime.strptime(runtime_str, format)
            runtime = timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
            return runtime
        except ValueError:
            pass

    return None


class IACollection(Enum):
    """Enum of valid collection ids for Internet Archive."""

    AUDIO_BOOKS_POETRY = "audio_bookspoetry"
    PODCASTS = "podcasts"
    PRESIDENTIAL_RECORDINGS = "presidential_recordings"


class IASearchQueryBuilder:
    """Query builder for the Internet Archive API."""

    media_type: Optional[str | List[str]] = None
    collection: Optional[str | List[str]] = None
    language: Optional[str | List[str]] = None

    def set_collection(self,
                       collection: IACollection | List[IACollection]) -> "IASearchQueryBuilder":
        if type(collection) is list:
            self.collection = [item.value for item in collection]
        else:
            self.collection = collection.value
        return self

    def set_language(self, language: str | List[str]) -> "IASearchQueryBuilder":
        self.language = language
        return self

    def set_media_type(self, media_type: str | List[str]) -> "IASearchQueryBuilder":
        self.media_type = media_type
        return self

    def __build_field_query(self,
                            field_name: str,
                            values: str | List[str],
                            operator: str = "OR") -> str:
        values = values if type(values) is list \
                        else [values]
        values_query = f" {operator} ".join(values)

        return f'{field_name}:({values_query})'

    def build_query(self) -> str:
        query_components = [
            self.__build_field_query("mediatype", self.media_type),
            self.__build_field_query("collection", self.collection),
            self.__build_field_query("language", self.language)
        ]

        query = " AND ".join(query_components)

        return query
