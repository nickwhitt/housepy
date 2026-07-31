PRAGMA foreign_keys = ON;

CREATE TABLE events (
    id          INTEGER PRIMARY KEY,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL DEFAULT 0 CHECK (month BETWEEN 0 AND 12),
    day         INTEGER NOT NULL DEFAULT 0 CHECK (day BETWEEN 0 AND 31),
    place       TEXT,
    name_given  TEXT,
    name_family TEXT,
    name_prefix TEXT,
    name_chosen TEXT,
    name_title  TEXT,
    name_suffix TEXT
);

CREATE TABLE houses (
    slug             TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    parent_slug      TEXT REFERENCES houses(slug) DEFERRABLE INITIALLY DEFERRED,
    founder_slug     TEXT REFERENCES people(slug) DEFERRABLE INITIALLY DEFERRED,
    founded_event_id INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    exiled_event_id  INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE titles (
    slug       TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    group_name TEXT
);

CREATE TABLE people (
    slug           TEXT PRIMARY KEY,
    name_given     TEXT,
    name_family    TEXT,
    name_prefix    TEXT,
    name_chosen    TEXT,
    name_title     TEXT,
    name_suffix    TEXT,
    birth_event_id INTEGER NOT NULL REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    death_event_id INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    house_slug     TEXT REFERENCES houses(slug) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE tenures (
    id                INTEGER PRIMARY KEY,
    person_slug       TEXT NOT NULL REFERENCES people(slug) DEFERRABLE INITIALLY DEFERRED,
    title_slug        TEXT NOT NULL REFERENCES titles(slug) DEFERRABLE INITIALLY DEFERRED,
    start_event_id    INTEGER NOT NULL REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    end_event_id      INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    ceremony_event_id INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    pretense          INTEGER NOT NULL DEFAULT 0 CHECK (pretense IN (0, 1)),
    regent_for_slug   TEXT REFERENCES people(slug) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE families (
    slug              TEXT PRIMARY KEY,
    father_slug       TEXT REFERENCES people(slug) DEFERRABLE INITIALLY DEFERRED,
    mother_slug       TEXT REFERENCES people(slug) DEFERRABLE INITIALLY DEFERRED,
    married_event_id  INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED,
    divorced_event_id INTEGER REFERENCES events(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE family_children (
    family_slug TEXT    NOT NULL REFERENCES families(slug) DEFERRABLE INITIALLY DEFERRED,
    child_slug  TEXT    NOT NULL REFERENCES people(slug) DEFERRABLE INITIALLY DEFERRED,
    position    INTEGER NOT NULL,
    PRIMARY KEY (family_slug, child_slug)
);

BEGIN TRANSACTION;
INSERT INTO "events" VALUES(1,1740,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(2,1719,12,15,'Darmstadt, Landgraviate of Hesse-Darmstadt',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(3,1790,4,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(4,1768,10,12,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(5,1751,10,16,'Prenzlau, Electorate of Brandenburg',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(6,1805,2,25,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(7,1753,6,14,'Prenzlau, Margraviate of Brandenburg',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(8,1830,4,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(9,1806,8,14,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(10,1790,4,6,NULL,NULL,NULL,NULL,'Ludwig X',NULL,NULL);
INSERT INTO "events" VALUES(11,1806,8,14,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES(12,1741,8,12,'Zweibrücken, Duchy of Palatinate-Zweibrücken',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "houses" VALUES('hesse','Hesse',NULL,NULL,NULL,NULL);
INSERT INTO "houses" VALUES('hesse-darmstadt','Hesse-Darmstadt','hesse','hesse-darmstadt.ludwig-ix',1,NULL);
INSERT INTO "titles" VALUES('hesse-darmstadt.landgrave','Landgrave of Hesse-Darmstadt',NULL);
INSERT INTO "titles" VALUES('hesse-and-by-rhine.grand-duke','Grand Duke of Hesse and by Rhine',NULL);
INSERT INTO "people" VALUES('hesse-darmstadt.ludwig-ix','Ludwig',NULL,NULL,'Ludwig IX',NULL,NULL,2,3,'hesse-darmstadt');
INSERT INTO "people" VALUES('hesse-darmstadt.friederike-luise','Friederike Luise','Hesse-Darmstadt','of',NULL,NULL,NULL,5,6,'hesse-darmstadt');
INSERT INTO "people" VALUES('hesse-darmstadt.ludwig-i','Ludwig',NULL,NULL,'Ludwig I',NULL,NULL,7,8,'hesse-darmstadt');
INSERT INTO "tenures" VALUES(1,'hesse-darmstadt.ludwig-ix','hesse-darmstadt.landgrave',4,NULL,NULL,0,NULL);
INSERT INTO "tenures" VALUES(2,'hesse-darmstadt.ludwig-i','hesse-and-by-rhine.grand-duke',9,NULL,NULL,0,NULL);
INSERT INTO "tenures" VALUES(3,'hesse-darmstadt.ludwig-i','hesse-darmstadt.landgrave',10,11,NULL,0,NULL);
INSERT INTO "families" VALUES('hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1','hesse-darmstadt.ludwig-ix','hesse-darmstadt.friederike-luise',12,NULL);
INSERT INTO "family_children" VALUES('hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1','hesse-darmstadt.ludwig-i',0);
COMMIT;
