/**
 *  "Site" definition tables
 *
 * Note: This is a SQLite port of the new SiteDB structure
 * only for testing the security module
 *
 **/

/* Site Tier as in T1, T2, T3 */
create table tier (
  id			number(10) not null,
  pos			number(10) not null,
  name			varchar(100) not null,
  --
  constraint pk_tier primary key (id),
  constraint uk_tier_pos unique (pos),
  constraint uk_tier_name unique (name)
);
/* NOT IN SQLITE: create sequence tier_sq increment by 1 start with 1;*/



/* Site definition and associated data */
create table site (
  id			INTEGER not null PRIMARY KEY  AUTOINCREMENT,
  name			varchar(100) not null,
  tier			number(10) not null,
  country		varchar(100) not null,
  gocdbid		number(10),
  usage			varchar(100),
  url			varchar(1000),
  logourl		varchar(1000),
  getdevlrelease	char(1),
  manualinstall		char(1),
  -- Probably going to need lots of othr ID's (SAM, Dashboard etc) so 
  -- maybe need a table for that, instead of making this one huge!
  --
  constraint uk_site unique (name),
  constraint fk_site_tier
    foreign key (tier) references tier (id)
    -- we don't delete tiers...
);
/* NOT IN SQLITE: create sequence site_sq increment by 1 start with 1;*/
create index ix_site_tier on site (tier);



/* How sites are related to one another e.g. FNAL is a parent site to Nebraska */
create table site_association (
  parent_site		number(10) not null,
  child_site		number(10) not null,
  --
  constraint pk_site_association primary key (parent_site, child_site),
  constraint fk_site_association_parent
    foreign key (parent_site) references site (id)
    on delete cascade,
  constraint fk_site_association_child
    foreign key (child_site) references site (id)
    on delete cascade
);
create index ix_site_association_child on site_association (child_site);



/* Site's official resource pledge */
create table resource_pledge (
  site			number(10) not null,
  cpu			float,
  disk_store		float,
  tape_store		float,
  wan_store		float,
  local_store		float,
  national_bandwidth	float,
  opn_bandwidth		float,
  status		char(1),
  --
  constraint pk_resource_pledge primary key (site),
  constraint fk_resource_pledge_site
    foreign key (site) references site (id)
    on delete cascade
);



/* Site's resource element (disks, storage)*/
create table resource_element (
  id			number(10) not null,
  site			number(10) not null,
  fqdn			varchar(200),
  type			varchar(100),
  is_primary		char(1),
  --
  constraint pk_resource_element primary key (id),
  constraint fk_resource_element_site
    foreign key (site) references site (id)
    on delete cascade
);
/* NOT IN SQLITE: create sequence resource_element_sq increment by 1 start with 1;*/
create index ix_resource_element_site on resource_element (site);



/* Site's phedex nodes */
create table phedex_node (
  id			number(10) not null,
  site			number(10) not null,
  name			varchar(100) not null,
  --
  constraint pk_phedex_node primary key (id),
  constraint uk_phedex_node_name unique (id, name),
  constraint fk_phedex_node_site
    foreign key (site) references site (id)
    -- cascade?  depends on how dependant phedex becomes on this...
);
/* NOT IN SQLITE: create sequence phedex_node_sq increment by 1 start with 1;*/
create index ix_phedex_node_site on phedex_node (site);
create index ix_phedex_node_name on phedex_node (name);



/**
 *   Site performance tables
 **/

/* High-level statistics about a site's performance */
create table performance (
  site			number(10) not null,
  time			timestamp not null,
  job_quality		float,
  transfer_quality	float,
  jobrobot_quality	float,
  job_io		float,
  wan_io		float,
  phedex_io		float,
  phedex_sum_tx_in	float,
  phedex_sum_tx_out	float,
  --
  constraint pk_performance primary key (site, time),
  constraint fk_performance_site
    foreign key (site) references site (id)
    on delete cascade
);



/* High-level statistics about a sites job activity */
create table job_activity (
  site			number(10) not null,
  time			timestamp not null,
  activity		varchar(100),
  num_jobs		number(10),
  --
  constraint pk_job_activity primary key (site, time),
  constraint fk_job_activity_site
    foreign key (site) references site (id)
    on delete cascade
);



/**
 *  "Person" definition tables
 **/

/* A human being */
create table contact (
  id			INTEGER not null PRIMARY KEY AUTOINCREMENT,
  surname		varchar(1000) not null,
  forename		varchar(1000) not null,
  email			varchar(1000) not null,
  username		varchar(60) not null,
  dn			varchar(1000),
  phone1		varchar(100),
  phone2		varchar(100),
  --
  -- constraint pk_contact primary key (id),
  constraint uk_contact_dn unique (dn)
);
/* NOT IN SQLITE: create sequence contact_sq increment by 1 start with 1;*/
create index ix_contact_surname on contact (surname);
create index ix_contact_forename on contact (forename);




/* Management roles e.g. 'PhedexSiteAdmin', 'PhedexDataManager' */
create table role (
  id			INTEGER  not null PRIMARY KEY AUTOINCREMENT,
  title			varchar(100) not null,
  --
  -- constraint pk_role primary key (id),
  constraint uk_role_title unique (title)
);
/* NOT IN SQLITE: create sequence role_sq increment by 1 start with 1;*/



/* An abstract group humans can belong to 
   e.g. 'higgs','top','BSM','global' etc. */
create table user_group (
  id			INTEGER not null PRIMARY KEY AUTOINCREMENT,
  name			varchar(100) not null,
  --
  -- constraint pk_user_group primary key (id), 
  constraint uk_user_group_name unique (name)
);
/* NOT IN SQLITE: create sequence user_group_sq increment by 1 start with 1;*/



/* A mapping of humans to responsibilites associated with a site 
   e.g. "Bob is the PhedexSiteAdmin of T4_Antartica" */
create table site_responsibility (
  contact		INTEGER not null,
  role			INTEGER not null,
  site			INTEGER not null,
  --
  constraint pk_site_resp primary key (contact, role, site),
  constraint fk_site_resp_contact
    foreign key (contact) references contact (id)
    on delete cascade,
  constraint fk_site_resp_role
    foreign key (role) references role (id)
    on delete cascade,
  constraint fk_site_resp_site
    foreign key (site) references site (id)
    on delete cascade
);
create index ix_site_resp_role on site_responsibility (role);
create index ix_site_resp_site on site_responsibility (site);



/* A mapping of humans to responsibilities associated with a group
   e.g. "Joe is the ProdRequestManager of the Gravitino group */
create table group_responsibility (
  contact		INTEGER not null,
  role			INTEGER not null,
  user_group		INTEGER not null,
  --
  constraint pk_group_resp_contact primary key (contact, role, user_group),
  constraint fk_group_resp_contact
    foreign key (contact) references contact (id)
    on delete cascade,
  constraint fk_group_resp_role
    foreign key (role) references role (id)
    on delete cascade,
  constraint fk_group_resp_user_group
    foreign key (user_group) references user_group (id)
    on delete cascade
);
create index ix_group_resp_role on group_responsibility (role);
create index ix_group_resp_user_group on group_responsibility (user_group);



/**
 *  Security Module tables
 **/

/* List of cryptographic keys for the security module */
create table crypt_key (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  cryptkey		varchar(80) not null,
  time			timestamp
);
/* NOT IN SQLITE: create sequence crypt_key_sq increment by 1 start with 1;*/
create index ix_crypt_key_cryptkey on crypt_key (cryptkey);
create index ix_crypt_key_time on crypt_key (time);



/* List of usernames and passwords for the secuirty module */
CREATE TABLE user_passwd (
<<<<<<< secmod.sql
     username VARCHAR(60) UNIQUE,
     description VARCHAR(60),
     passwd VARCHAR(30)
=======
  username		varchar(60) not null,
  passwd		varchar(30) not null,
  --
  -- constraint pk_user_passwd primary key (contact),
  constraint uk_user_passwd_username unique (username),
  constraint fk_user_passwd_contact
    -- foreign key (contact) references contact (id)
    -- on delete cascade
);



/**
 *  Generic survey tables
 **/

/* Defines a survey and associates it with its creator */
create table survey (
  id			number(10) not null,
  name			varchar(100) not null,
  creator		number(10),
  opened		timestamp,
  closed		timestamp,
  --
  constraint pk_survey primary key (id),
  constraint fk_survey_creator
    foreign key (creator) references contact (id)
    on delete set null
);
/* NOT IN SQLITE: create sequence survey_sq increment by 1 start with 1;*/
create index ix_survery_creator on survey (creator);



/* For sending out surveys by tier */
create table survey_tiers (
  survey		number(10) not null,
  tier			number(10) not null,
  --
  constraint fk_survey_tiers_survey
    foreign key (survey) references survey (id)
    on delete cascade,
  constraint fk_survey_tiers_tier
    foreign key (tier) references tier (id)
    -- we don't delete tiers
>>>>>>> 1.3
);
create index ix_survey_tiers_survey on survey_tiers (survey);
create index ix_survey_tiers_tier on survey_tiers (tier);



/* For sending out surveys by role */
create table survey_roles (
  survey		number(10) not null,
  role			number(10) not null,
  --
  constraint fk_survey_roles_survey
    foreign key (survey) references survey (id)
    on delete cascade,
  constraint fk_survey_roles_role
    foreign key (role) references role (id)
    on delete cascade
);
create index ix_survey_roles_survey on survey_roles (survey);
create index ix_survey_roles_role on survey_roles (role);



/* A question on a survey */
create table question (
  id			number(10) not null,
  survey		number(10) not null,
  question		varchar(4000) not null,
  form_type		varchar(100) not null,
  --
  constraint pk_question primary key (id),
  constraint fk_question_survey
    foreign key (survey) references survey (id)
    on delete cascade
);
/* NOT IN SQLITE: create sequence question_sq increment by 1 start with 1;*/
create index ix_question_survey on question (survey);



/* A default answer on a survey (for checkbox or drop-down menu style questions) */
create table question_default (
  question		number(10) not null,
  pos			number(10) not null,
  value			varchar(4000) not null,
  --
  constraint pk_question_default primary key (question, pos),
  constraint fk_question_default_question
    foreign key (question) references question (id)
    on delete cascade
);



/* A site's answer to the survey question */
create table question_answer (
  site			number(10) not null,
  question		number(10) not null,
  answer		varchar(4000) not null,
  --
  constraint pk_question_answer primary key (site, question),
  constraint fk_question_answer_site
    foreign key (site) references site (id)
    on delete cascade,
  constraint fk_question_answer_question
    foreign key (question) references question (id)
    on delete cascade
);
create index ix_question_answer_question on question_answer (question);
