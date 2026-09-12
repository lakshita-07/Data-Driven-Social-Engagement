# Data dictionary

## Posts

| Field | Meaning |
|---|---|
| `post_id` | Unique YouTube video identifier |
| `content_type` | Short or Long-form |
| `caption` | Video title/description text used for topic classification |
| `posting_datetime` | Publication timestamp |
| `duration_seconds` | Video duration |
| `views` | Cumulative public view count |
| `likes` | Cumulative public like count |
| `comments_count` | Cumulative public comment count |
| `like_rate` | Likes divided by views, expressed as a percentage |
| `comment_rate` | Comments divided by views, expressed as a percentage |
| `engagement_rate` | Likes plus comments divided by views, expressed as a percentage |
| `posting_hour` | Hour extracted from the publication timestamp |
| `posting_day` | Day name extracted from the publication timestamp |
| `is_weekend` | Whether the publication date falls on Saturday or Sunday |
| `caption_length` | Number of characters in the caption |
| `hashtag_count` | Number of hashtag tokens in the hashtag field |
| `video_length_group` | 0-30, 31-60, or 60+ seconds |
| `virality_score` | Weighted score when shares/saves exist; otherwise an engagement-reach proxy |
| `topic` | Rule-based topic assigned from caption keywords |

## Comments

| Field | Meaning |
|---|---|
| `comment_id` | Unique comment identifier |
| `post_id` | ID of the post receiving the comment |
| `comment_text` | Original comment text |
| `cleaned_text` | Lowercase, URL-cleaned analysis text |
| `polarity` | TextBlob sentiment polarity from -1 to 1 |
| `sentiment` | Positive, Neutral, or Negative |
| `relatability_score` | Rule-based relatability score |
| `relatability` | Relatable or Neutral classification |

All engagement values are observational cumulative counts. Missing YouTube
shares, saves, and retention values are kept missing rather than invented.
