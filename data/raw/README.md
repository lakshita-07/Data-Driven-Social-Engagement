# Raw data

Place source exports and API downloads in this directory for local processing.
Raw data is ignored by Git by default because it may contain private or
redistributable source material. Keep only documentation and directory markers
tracked in the repository.

## Public YouTube files

`youtube_videos_raw.csv` is collected by `src/data_collection/youtube_api.py`
from a public channel's uploads playlist. It contains video metadata and public
view, like, and comment counts.

`youtube_comments_raw.csv` is collected by `src/data_collection/youtube_comments.py`
from the top-level comments exposed by the public YouTube Data API. Both files
include `source_type=public_youtube_api`.

This project uses a third-party public channel, not an owned YouTube channel.
The YouTube Analytics API owner-only metrics are unavailable: shares, saves or
playlist additions, retention or average view percentage, and subscribers
gained. These values must remain unavailable (`NaN`/blank), never fabricated or
replaced with realistic-looking zeros.
