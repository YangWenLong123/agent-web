-- 在 MYSQL_DATABASE 指定的库内执行，启动时自动创建缺少的表。
CREATE TABLE IF NOT EXISTS conversations (
    id CHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
    title VARCHAR(128) NOT NULL,
    created_at VARCHAR(40) NOT NULL,
    updated_at VARCHAR(40) NOT NULL,
    INDEX conversations_updated (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS turns (
    id CHAR(32) CHARACTER SET ascii COLLATE ascii_bin PRIMARY KEY,
    sequence_no BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    conversation_id CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    content LONGTEXT NOT NULL,
    answer LONGTEXT NOT NULL,
    raw_json LONGTEXT NOT NULL,
    result_json LONGTEXT NULL,
    status VARCHAR(16) NOT NULL,
    error TEXT NOT NULL,
    stream_id CHAR(32) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
    model VARCHAR(128) NOT NULL,
    usage_json LONGTEXT NULL,
    context_count INT UNSIGNED NOT NULL DEFAULT 0,
    created_at VARCHAR(40) NOT NULL,
    updated_at VARCHAR(40) NOT NULL,
    UNIQUE KEY turns_sequence (sequence_no),
    INDEX turns_conversation (conversation_id, sequence_no),
    CONSTRAINT turns_conversation_fk FOREIGN KEY (conversation_id) REFERENCES conversations(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
