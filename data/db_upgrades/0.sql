CREATE TABLE IF NOT EXISTS `notebooks` (
    `localId` INTEGER PRIMARY KEY AUTOINCREMENT,
    `guid` TEXT,
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
    `localId` INTEGER PRIMARY KEY AUTOINCREMENT,
    `guid` TEXT,
    `name` TEXT,
    `updateSequenceNum` INTEGER DEFAULT 0,
    `parentGuid` BOOL,
    `dirty` BOOL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS `notes` (
    `localId` INTEGER PRIMARY KEY AUTOINCREMENT,
    `guid` TEXT,
    `title` TEXT,
    `content` TEXT,
    `contentHash` TEXT,
    `contentLength` INTEGER,
    `created` INTEGER,
    `updated` INTEGER,
    `deleted` INTEGER,
    `active` BOOL,
    `updateSequenceNum` INTEGER DEFAULT 0,
    `notebookGuid` TEXT,
    `parentGuid` BOOL,
    `dirty` BOOL DEFAULT 0
);

REPLACE INTO `global_data` (`key`, `value`) VALUES ("version", "1");
