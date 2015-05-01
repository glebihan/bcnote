CREATE TABLE IF NOT EXISTS `notebooks` (
    `guid` TEXT PRIMARY KEY,
    `name` TEXT,
    `updateSequenceNum` INTEGER DEFAULT 0,
    `defaultNotebook` BOOL,
    `serviceCreated` INTEGER,
    `serviceUpdated` INTEGER,
    `published` BOOL,
    `stack` TEXT,
    `dirty` BOOL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS `tags` (
    `guid` TEXT PRIMARY KEY,
    `name` TEXT,
    `updateSequenceNum` INTEGER DEFAULT 0,
    `parentGuid` BOOL,
    `dirty` BOOL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS `notes` (
    `guid` TEXT PRIMARY KEY,
    `title` TEXT,
    `content` TEXT,
    `contentHash` TEXT,
    `contentLength` INTEGER,
    `created` INTEGER,
    `updated` INTEGER,
    `deleted` INTEGER,
    `active` BOOL DEFAULT 1,
    `updateSequenceNum` INTEGER DEFAULT 0,
    `notebookGuid` TEXT,
    `dirty` BOOL DEFAULT 0
);

REPLACE INTO `global_data` (`key`, `value`) VALUES ("version", "1");
