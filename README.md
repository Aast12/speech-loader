# Speech Loader

The projects crawls over audio files from the [Internet Archive](https://archive.org/)
and stores features for further applications on machine learning models.

The project is made out of the following components:

- Object Storage: All processed audio files are stored in object storage for retrieval, e.g. to stream audio data during a model training. Current implementation stores data in the local disk.
- Tabular database: A database to store extracted features and references to the downloaded audio files. Current implementation uses Postgres.
- Crawler: A process that receives query parameters to search files in the Internet Archive.

The `IACrawler` can receive query parameters to perform different searches on each execution, and avoids re-processing of items already existing in the database.

## Development

The project can run from the docker compose file:

```bash
docker compose up
```

Can be executed by installing the python dependencies and ffmpeg (dependency of pydub, used for audio features).

```bash
pip install -r requirements.txt
python main.py
```

