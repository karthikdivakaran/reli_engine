BEGIN TRANSACTION;
DROP TABLE IF EXISTS "FailureRate";
CREATE TABLE FailureRate (
        RateID INTEGER PRIMARY KEY,
        ComponentID INTEGER,
        RateValue REAL,
        CalculatedDate TEXT,
        FOREIGN KEY(ComponentID) REFERENCES Component(ComponentID)
    );
DROP TABLE IF EXISTS "Project";
CREATE TABLE Project (
        ProjectID INTEGER PRIMARY KEY,
        ProjectName TEXT,
        Description TEXT,
        CreatedDate DATETIME,
        LastModified  DATETIME,
        UserID INTEGER,
        FOREIGN KEY(UserID) REFERENCES User(UserID)
    );
DROP TABLE IF EXISTS "ReliabilityCalculation";
CREATE TABLE ReliabilityCalculation (
        CalcID INTEGER PRIMARY KEY,
        ProjectID INTEGER,
        ReliabilityValue REAL,
        CalculationDate TEXT,
        FOREIGN KEY(ProjectID) REFERENCES Project(ProjectID)
    );
DROP TABLE IF EXISTS "Report";
CREATE TABLE Report (
        ReportID INTEGER PRIMARY KEY,
        ProjectID INTEGER,
        GeneratedDate TEXT,
        FileType TEXT,
        FOREIGN KEY(ProjectID) REFERENCES Project(ProjectID)
    );
DROP TABLE IF EXISTS "User";
CREATE TABLE User (
        UserID INTEGER PRIMARY KEY,
        Name TEXT,
        Email TEXT,
        Password TEXT
    );
DROP TABLE IF EXISTS "components";
CREATE TABLE "components" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
    "type" TEXT,
    "reference" TEXT DEFAULT "nil",
    "refFIT" INTEGER,
    "theetta1" INTEGER
);
DROP TABLE IF EXISTS "temp_factor";
CREATE TABLE "temp_factor" (
	"id"	INTEGER,
	"component"	TEXT,
	"theetta1"	INTEGER,
	"theetta2"	INTEGER,
	"PiT"	REAL
);
INSERT INTO "Project" ("ProjectID","ProjectName","Description","CreatedDate","LastModified","UserID") VALUES (1,'test','123','2025-02-05 19:28:56','2025-02-05 19:28:56',1),
 (2,'new project','test data','2025-02-05 20:00:56','2025-02-05 20:00:56',1),
 (3,'test','123','2025-02-05 20:05:59','2025-02-05 20:05:59',1);
INSERT INTO "components" ("name","type","reference","refFIT","theetta1") VALUES ('resistors','carbon film','less 100',0.3,55),
 ('resistors','carbon film','great 100',1,55),
 ('resistors','metal film ','nil',0.2,55),
 ('resistors','film circuits','standard',0.1,55),
 ('resistors','film circuits','custom design',0.5,55),
 ('resistors','metal oxide','nil',5,85),
 ('resistors','wire wound','nil',5,85),
 ('resistors','variable','nil',30,55);
INSERT INTO "temp_factor" ("id","component","theetta1","theetta2","PiT") VALUES (1,'resistors',55,25,0.49),
 (2,'resistors',55,30,0.56),
 (3,'resistors',55,40,0.71),
 (4,'resistors',55,50,0.89),
 (5,'resistors',55,60,1.1),
 (6,'resistors',55,70,1.4),
 (7,'resistors',55,80,1.8),
 (8,'resistors',55,90,2.2),
 (9,'resistors',55,100,2.8),
 (10,'resistors',55,110,3.6),
 (11,'resistors',55,120,4.6),
 (12,'resistors',55,125,5.1),
 (13,'resistors',85,25,0.25),
 (14,'resistors',85,30,0.28),
 (15,'resistors',85,40,0.35),
 (16,'resistors',85,50,0.45),
 (17,'resistors',85,60,0.56),
 (18,'resistors',85,70,0.71),
 (19,'resistors',85,80,0.89),
 (20,'resistors',85,90,1.1),
 (21,'resistors',85,100,1.4),
 (22,'resistors',85,110,1.8),
 (23,'resistors',85,120,2.3),
 (24,'resistors',85,125,2.6),
 (25,'inductors',55,25,0.79),
 (26,'inductors',55,30,0.82),
 (27,'inductors',55,40,0.89),
 (28,'inductors',55,50,0.96),
 (29,'inductors',55,60,1.1),
 (30,'inductors',55,70,1.2),
 (31,'inductors',55,80,1.5),
 (32,'inductors',55,90,2.3),
 (33,'inductors',55,100,4.3),
 (34,'inductors',55,110,8.8),
 (35,'inductors',55,120,19.0),
 (36,'inductors',55,125,29.0),
 (37,'inductors',60,25,0.75),
 (38,'inductors',60,30,0.78),
 (39,'inductors',60,40,0.84),
 (40,'inductors',60,50,0.91),
 (41,'inductors',60,60,1.0),
 (42,'inductors',60,70,1.1),
 (43,'inductors',60,80,1.5),
 (44,'inductors',60,90,2.2),
 (45,'inductors',60,100,4.0),
 (46,'inductors',60,110,8.4),
 (47,'inductors',60,120,18.0),
 (48,'inductors',60,125,27.0),
 (49,'inductors',85,25,0.43),
 (50,'inductors',85,30,0.44),
 (51,'inductors',85,40,0.48),
 (52,'inductors',85,50,0.52),
 (53,'inductors',85,60,0.57),
 (54,'inductors',85,70,0.66),
 (55,'inductors',85,80,0.83),
 (56,'inductors',85,90,1.3),
 (57,'inductors',85,100,2.3),
 (58,'inductors',85,110,4.8),
 (59,'inductors',85,120,10.0),
 (60,'inductors',85,125,15.0),
 (61,'Transformers',55,25,0.79),
 (62,'Transformers',55,30,0.82),
 (63,'Transformers',55,40,0.89),
 (64,'Transformers',55,50,0.96),
 (65,'Transformers',55,60,1.1),
 (66,'Transformers',55,70,1.2),
 (67,'Transformers',55,80,1.5),
 (68,'Transformers',55,90,2.3),
 (69,'Transformers',55,100,4.3),
 (70,'Transformers',55,110,8.8),
 (71,'Transformers',55,120,19.0),
 (72,'Transformers',55,125,29.0),
 (73,'Transformers',60,25,0.75),
 (74,'Transformers',60,30,0.78),
 (75,'Transformers',60,40,0.84),
 (76,'Transformers',60,50,0.91),
 (77,'Transformers',60,60,1.0),
 (78,'Transformers',60,70,1.1),
 (79,'Transformers',60,80,1.5),
 (80,'Transformers',60,90,2.2),
 (81,'Transformers',60,100,4.0),
 (82,'Transformers',60,110,8.4),
 (83,'Transformers',60,120,18.0),
 (84,'Transformers',60,125,27.0),
 (85,'Transformers',85,25,0.43),
 (86,'Transformers',85,30,0.44),
 (87,'Transformers',85,40,0.48),
 (88,'Transformers',85,50,0.52),
 (89,'Transformers',85,60,0.57),
 (90,'Transformers',85,70,0.66),
 (91,'Transformers',85,80,0.83),
 (92,'Transformers',85,90,1.3),
 (93,'Transformers',85,100,2.3),
 (94,'Transformers',85,110,4.8),
 (95,'Transformers',85,120,10.0),
 (96,'Transformers',85,125,15.0);
COMMIT;
