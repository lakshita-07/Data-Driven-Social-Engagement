import pandas as pd

from src.data_collection.youtube_api import RAW_COLUMNS as VIDEO_COLUMNS
from src.data_collection.youtube_api import save_rows as save_video_rows
from src.data_collection.youtube_comments import RAW_COLUMNS as COMMENT_COLUMNS
from src.data_collection.youtube_comments import save_rows as save_comment_rows


def test_youtube_raw_schemas(tmp_path):
    video_path = tmp_path / "youtube_videos_raw.csv"
    comment_path = tmp_path / "youtube_comments_raw.csv"
    save_video_rows([], video_path)
    save_comment_rows([], comment_path)
    assert pd.read_csv(video_path).columns.tolist() == VIDEO_COLUMNS
    assert pd.read_csv(comment_path).columns.tolist() == COMMENT_COLUMNS


def test_youtube_raw_source_type_when_rows_exist(tmp_path):
    video_path = tmp_path / "youtube_videos_raw.csv"
    comment_path = tmp_path / "youtube_comments_raw.csv"
    save_video_rows([{"source_type": "public_youtube_api"}], video_path)
    save_comment_rows([{"source_type": "public_youtube_api"}], comment_path)
    assert pd.read_csv(video_path)["source_type"].eq("public_youtube_api").all()
    assert pd.read_csv(comment_path)["source_type"].eq("public_youtube_api").all()