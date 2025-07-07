CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    expert INTEGER NOT NULL,
    admin INTEGER NOT NULL
);
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_text TEXT NOT NULL,
    answer_text TEXT,
    answer_by_id INTEGER NOT NULL,
    expert_id INTEGER NOT NULL
);