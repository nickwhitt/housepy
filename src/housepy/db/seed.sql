BEGIN TRANSACTION;
INSERT INTO "events" VALUES('hesse-darmstadt+founded',1740,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-ix+birth',1719,12,15,'Darmstadt, Landgraviate of Hesse-Darmstadt',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-ix+death',1790,4,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-ix+hesse-darmstadt.landgrave+start',1768,10,12,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.friederike-luise+birth',1751,10,16,'Prenzlau, Electorate of Brandenburg',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.friederike-luise+death',1805,2,25,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-i+birth',1753,6,14,'Prenzlau, Margraviate of Brandenburg',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-i+death',1830,4,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-i+hesse-and-by-rhine.grand-duke+start',1806,8,14,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-i+hesse-darmstadt.landgrave+start',1790,4,6,NULL,NULL,NULL,NULL,'Ludwig X',NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-i+hesse-darmstadt.landgrave+end',1806,8,14,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "events" VALUES('hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1+married',1741,8,12,'Zweibrücken, Duchy of Palatinate-Zweibrücken',NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "houses" VALUES('hesse','Hesse',NULL,NULL,NULL,NULL);
INSERT INTO "houses" VALUES('hesse-darmstadt','Hesse-Darmstadt','hesse','hesse-darmstadt.ludwig-ix','hesse-darmstadt+founded',NULL);
INSERT INTO "titles" VALUES('hesse-darmstadt.landgrave','Landgrave of Hesse-Darmstadt',NULL);
INSERT INTO "titles" VALUES('hesse-and-by-rhine.grand-duke','Grand Duke of Hesse and by Rhine',NULL);
INSERT INTO "people" VALUES('hesse-darmstadt.ludwig-ix','Ludwig',NULL,NULL,'Ludwig IX',NULL,NULL,'hesse-darmstadt.ludwig-ix+birth','hesse-darmstadt.ludwig-ix+death','hesse-darmstadt','male');
INSERT INTO "people" VALUES('hesse-darmstadt.friederike-luise','Friederike Luise','Hesse-Darmstadt','of',NULL,NULL,NULL,'hesse-darmstadt.friederike-luise+birth','hesse-darmstadt.friederike-luise+death','hesse-darmstadt','female');
INSERT INTO "people" VALUES('hesse-darmstadt.ludwig-i','Ludwig',NULL,NULL,'Ludwig I',NULL,NULL,'hesse-darmstadt.ludwig-i+birth','hesse-darmstadt.ludwig-i+death','hesse-darmstadt','male');
INSERT INTO "tenures" VALUES(1,'hesse-darmstadt.ludwig-ix','hesse-darmstadt.landgrave','hesse-darmstadt.ludwig-ix+hesse-darmstadt.landgrave+start',NULL,NULL,0,NULL);
INSERT INTO "tenures" VALUES(2,'hesse-darmstadt.ludwig-i','hesse-and-by-rhine.grand-duke','hesse-darmstadt.ludwig-i+hesse-and-by-rhine.grand-duke+start',NULL,NULL,0,NULL);
INSERT INTO "tenures" VALUES(3,'hesse-darmstadt.ludwig-i','hesse-darmstadt.landgrave','hesse-darmstadt.ludwig-i+hesse-darmstadt.landgrave+start','hesse-darmstadt.ludwig-i+hesse-darmstadt.landgrave+end',NULL,0,NULL);
INSERT INTO "families" VALUES('hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1','hesse-darmstadt.ludwig-ix','hesse-darmstadt.friederike-luise','hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1+married',NULL);
INSERT INTO "family_children" VALUES('hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1','hesse-darmstadt.ludwig-i',0);
COMMIT;

BEGIN TRANSACTION;
INSERT INTO houses (slug, name) VALUES ("windsor", "Windsor");
INSERT INTO houses (slug, name) VALUES ("glucksburg", "Glücksburg");

INSERT INTO titles (slug, name) VALUES ('united-kingdom.king', 'King of the United Kingdom');
INSERT INTO titles (slug, name) VALUES ('united-kingdom.queen', 'Queen of the United Kingdom');
INSERT INTO titles (slug, name) VALUES ('edinburgh.duke', 'Duke of Edinburgh');

INSERT INTO events (slug, year, month, day, place, name_chosen, name_prefix, name_family)
    VALUES ('windsor.elizabeth-ii+birth', 1926, 4, 21, 'Mayfair, London, England', 'Elizabeth', 'of', 'York');
INSERT INTO events (slug, year, month, day) VALUES ('windsor.elizabeth-ii+death', 2022, 9, 8);
INSERT INTO people (slug, name_chosen, name_given, birth_event_slug, death_event_slug, house_slug, sex)
    VALUES ('windsor.elizabeth-ii', 'Elizabeth II', 'Elizabeth Alexandra Mary', 'windsor.elizabeth-ii+birth', 'windsor.elizabeth-ii+death', 'windsor', 'female');
INSERT INTO events (slug, year, month, day) VALUES ('windsor.elizabeth-ii+united-kingdom.queen+start', 1952, 2, 6);
INSERT INTO tenures (person_slug, title_slug, start_event_slug, pretense) VALUES ('windsor.elizabeth-ii', 'united-kingdom.queen', 'windsor.elizabeth-ii+united-kingdom.queen+start', 0);

INSERT INTO events (slug, year, month, day, place, name_chosen, name_prefix, name_family)
    VALUES ('mountbatten.philip+birth', 1921, 6, 10, 'Mon Repos, Corfu, Greece', 'Philip', 'of', 'Glücksburg');
INSERT INTO events (slug, year, month, day) VALUES ('mountbatten.philip+death', 2021, 4, 9);
INSERT INTO people (slug, name_given, name_family, birth_event_slug, death_event_slug, house_slug, sex)
    VALUES ('mountbatten.philip', 'Philip', 'Mountbatten', 'mountbatten.philip+birth', 'mountbatten.philip+death', 'glucksburg', 'male');
INSERT INTO events (slug, year, month, day) VALUES ('mountbatten.philip+edinburgh.duke+start', 1947, 11, 20);
INSERT INTO tenures (person_slug, title_slug, start_event_slug, pretense) VALUES ('mountbatten.philip', 'edinburgh.duke', 'mountbatten.philip+edinburgh.duke+start', 0);

INSERT INTO events (slug, year, month, day, place) VALUES ('mountbatten.philip+windsor.elizabeth-ii+family+marriage', 1947, 11, 20, "Westminster Abbey, London, England");
INSERT INTO families (slug, father_slug, mother_slug, married_event_slug)
    VALUES ('mountbatten.philip+windsor.elizabeth-ii+family', 'mountbatten.philip', 'windsor.elizabeth-ii', 'mountbatten.philip+windsor.elizabeth-ii+family+marriage');

INSERT INTO events (slug, year, month, day, place, name_chosen, name_prefix, name_family)
    VALUES ('windsor.charles-iii+birth', 1948, 11, 14, 'Buckingham Palace, London, England', 'Charles', 'of', 'Edinburgh');
INSERT INTO people (slug, name_chosen, name_given, birth_event_slug, house_slug, sex)
    VALUES ('windsor.charles-iii', 'Charles III', 'Charles Philip Arthur George', 'windsor.charles-iii+birth', 'windsor', 'male');
INSERT INTO events (slug, year, month, day) VALUES ('windsor.charles-iii+united-kingdom.king+start', 2022, 9, 8);
INSERT INTO tenures (person_slug, title_slug, start_event_slug, pretense) VALUES ('windsor.charles-iii', 'united-kingdom.king', 'windsor.charles-iii+united-kingdom.king+start', 0);

INSERT INTO family_children VALUES('mountbatten.philip+windsor.elizabeth-ii+family', 'windsor.charles-iii', 0);
COMMIT;
