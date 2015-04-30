CREATE TABLE IF NOT EXISTS `notebooks` (
    `localID` INTEGER PRIMARY KEY AUTOINCREMENT,
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

REPLACE INTO `global_data` (`key`, `value`) VALUES ("version", "1");
