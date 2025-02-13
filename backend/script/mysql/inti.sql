CREATE DATABASE AIGC;
USE AIGC;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    avatar TEXT
);

CREATE TABLE user_story (
    username VARCHAR(255),
    storyId VARCHAR(255),
    saved VARCHAR(20)
);

CREATE TABLE paragraphs (
    storyId VARCHAR(255),
    prompt TEXT,
    `text` TEXT,
    url TEXT,
    weight INT
);

CREATE TABLE total_story (
    storyId VARCHAR(255),
    outline TEXT,
    originalStory TEXT
);

