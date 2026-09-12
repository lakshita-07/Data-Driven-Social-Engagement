CREATE TABLE IF NOT EXISTS posts (
    post_id VARCHAR(32) PRIMARY KEY,
    platform VARCHAR(32) NOT NULL,
    account_id VARCHAR(128),
    content_type VARCHAR(32),
    caption TEXT,
    hashtags TEXT,
    posting_datetime DATETIME NULL,
    duration_seconds INT NULL,
    views BIGINT NULL,
    likes BIGINT NULL,
    comments_count BIGINT NULL,
    shares BIGINT NULL,
    saves BIGINT NULL,
    retention_rate DOUBLE NULL,
    source_type VARCHAR(64) DEFAULT 'public_youtube_api'
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id VARCHAR(64) PRIMARY KEY,
    post_id VARCHAR(32) NOT NULL,
    comment_text TEXT,
    comment_datetime DATETIME NULL,
    comment_like_count BIGINT NULL,
    author_channel_id VARCHAR(128),
    source_type VARCHAR(64) DEFAULT 'public_youtube_api',
    CONSTRAINT fk_comments_posts
        FOREIGN KEY (post_id) REFERENCES posts(post_id)
        ON DELETE CASCADE
);
