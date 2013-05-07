INSERT INTO contact (dn,surname,forename,email,username) VALUES ('/O=GRID-FR/C=CH/O=CSCS/OU=CC-LCG/CN=Derek Feichtinger','Feichtinger','Derek','derek.feichtinger@psi.ch','dfeichti');
INSERT INTO contact (dn,surname,forename,email,username) VALUES ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=dfeich/CN=613756/CN=Derek Feichtinger','Feichtinger','Derek','derek.feichtinger@cern.ch','dfeich');
INSERT INTO contact (dn,surname,forename,email,username) VALUES ('/C=UK/O=eScience/OU=Bristol/L=IS/CN=simon metson','Metson','Simon','simon.metson@cern.ch','metson');
INSERT INTO contact (dn,surname,forename,email,username) VALUES ('/DC=org/DC=doegrids/OU=People/CN=Ricky Egeland 693921','Egeland','Ricky','Ricky.Egeland@cern.ch','egeland');
INSERT INTO contact (dn,surname,forename,email,username) VALUES ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=eulisse/CN=607460/CN=Giulio Eulisse','Eulisse','Giulio','Giulio.Eulisse@cern.ch','eulisse');

INSERT INTO role (title) VALUES ('CentralOps');
INSERT INTO role (title) VALUES ('ProdManager');
INSERT INTO role (title) VALUES ('PhedexDataManager');
INSERT INTO role (title) VALUES ('PhedexSiteAdmin');

INSERT INTO site (name,tier,country) VALUES ('NONE',0,'NOWHERE');
INSERT INTO site (name,tier,country) VALUES ('T2_CSCS',2,'CH');
INSERT INTO site (name,tier,country) VALUES ('T2_TestsiteA',2,'SOMEWHERE');

INSERT INTO user_group (name) VALUES ('global');
INSERT INTO user_group (name) VALUES ('higgs');

INSERT INTO site_responsibility (contact,role,site) VALUES (1,4,2);
INSERT INTO site_responsibility (contact,role,site) VALUES (1,4,3);

INSERT INTO group_responsibility (contact,role,user_group) VALUES (1,1,1);
INSERT INTO group_responsibility (contact,role,user_group) VALUES (1,2,2);


INSERT INTO crypt_key (cryptkey) VALUES ('T05FIGVmZ2hpamtsbW5vcHFyc3R1dnd4eXphYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5emFiZGU=');

INSERT INTO user_passwd (username,passwd) VALUES ('dfeichti','ghm91Wx98jzJA');
INSERT INTO user_passwd (username,passwd) VALUES ('dfeich','AAIRyHeTE4eg.');
INSERT INTO user_passwd (username,passwd) VALUES ('unsigned','usUUgS8qb/VL.');

