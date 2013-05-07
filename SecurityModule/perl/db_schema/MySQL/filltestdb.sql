INSERT INTO auth_n_user (dn,username) VALUES ('/O=GRID-FR/C=CH/O=CSCS/OU=CC-LCG/CN=Derek Feichtinger','dfeichti');
INSERT INTO auth_n_user (dn,username) VALUES ('/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=dfeich/CN=613756/CN=Derek Feichtinger','dfeich');

INSERT INTO auth_z_role (role) VALUES ('CentralOps');
INSERT INTO auth_z_role (role) VALUES ('ProdManager');
INSERT INTO auth_z_role (role) VALUES ('DataManager');
INSERT INTO auth_z_role (role) VALUES ('SiteAdmin');

INSERT INTO auth_z_scope (scope) VALUES ('NONE');
INSERT INTO auth_z_scope (scope) VALUES ('T2_CSCS');
INSERT INTO auth_z_scope (scope) VALUES ('T2_TestsiteA');


INSERT INTO auth_z_user_role (user_id,role_id,scope_id) VALUES (1,1,1);
INSERT INTO auth_z_user_role (user_id,role_id,scope_id) VALUES (1,4,2);
INSERT INTO auth_z_user_role (user_id,role_id,scope_id) VALUES (1,4,3);

INSERT INTO crypt_key (cryptkey) VALUES ('ONE efghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabde');
INSERT INTO crypt_key (cryptkey) VALUES ('TWO efghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabde');
INSERT INTO crypt_key (cryptkey) VALUES ('THREE ghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabde');

# passwords for these test users are identical to username
INSERT INTO user_passwd (username,passwd) VALUES ('dfeich','AAIRyHeTE4eg.');
INSERT INTO user_passwd (username,passwd) VALUES ('dfeichti','ghm91Wx98jzJA');

