/**
 *  "Site" definition tables
 **/

/* Site Tier as in T1, T2, T3 */
create table tier (
  id			INTEGER PRIMARY KEY  AUTOINCREMENT,
  pos			float not null,
  name		varchar(100) not null,
  --
  constraint uk_tier_pos unique (pos),
  constraint uk_tier_name unique (name)
);

/* Site definition and associated data */
/**
 * Tables to support naming convention
 **/ 
create table cms_name(
	id			INTEGER PRIMARY KEY  AUTOINCREMENT,
	name		varchar(100) not null,
  constraint uk_site unique (name)
);

create table sam_name (
	id			INTEGER PRIMARY KEY AUTOINCREMENT,
	name			varchar(100) not null,
  gocdbid		float, 
  constraint uk_site unique (name)	
);

create table site_cms_name_map(
	site_id			INTEGER not null,
	cms_name_id			INTEGER not null,
	constraint fk_naming_site_cms_id
    foreign key (cms_name_id) references cms_name (id),
  constraint fk_naming_site_id
    foreign key (site_id) references site (id)
);

create table resource_cms_name_map(
	resource_id			INTEGER not null,
	cms_name_id			INTEGER not null,
	constraint fk_naming_resource_cms_id
    foreign key (cms_name_id) references cms_name (id),
  constraint fk_naming_resource_id
    foreign key (resource_id) references resource_element (id)
);

create table PHEDEX_NODE_CMS_NAME_MAP(
	NODE_ID             INTEGER not null,
	CMS_NAME_ID         INTEGER not null,
  constraint fk_naming_resource_cms_id 
    foreign key (cms_name_id) references cms_name (id),
  constraint fk_naming_resource_id
    foreign key (NODE_ID) references phedex_node (id)
);

create table sam_cms_name_map(
	sam_id			INTEGER not null,
	cms_name_id			INTEGER not null,
	constraint fk_naming_sam_cms_id
    foreign key (cms_name_id) references cms_name (id),
  constraint fk_naming_sam_id
    foreign key (sam_id) references sam_name (id)
);

/**
 * Table describing a site
 **/
create table site (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  name			varchar(100) not null,
  tier			INTEGER not null,
  country		varchar(100) not null,
  gocdbid		float,
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
create index ix_site_tier on site (tier);

/* How sites are related to one another e.g. FNAL is a parent site to Nebraska */
create table site_association (
  parent_site		INTEGER not null,
  child_site		INTEGER not null,
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
  pledgeid          	INTEGER PRIMARY KEY AUTOINCREMENT,
  site					float not null,
  pledgedate			timestamp,
  pledgequarter			float,
  cpu					float,
  job_slots				float,  
  disk_store			float,
  tape_store			float,
  wan_store				float,
  local_store			float,
  national_bandwidth	float,
  opn_bandwidth			float,
  status				char(1),
  --
  constraint fk_resource_pledge_site
    foreign key (site) references site (id)
    on delete cascade
);
CREATE TRIGGER insert_resource_pledge_pledgedate AFTER INSERT ON resource_pledge
BEGIN
  UPDATE resource_pledge SET pledgedate = DATETIME('NOW')
  WHERE rowid = new.rowid;
END;


/* Site's resource element (disks, storage)*/
create table resource_element (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  site			INTEGER not null,
  fqdn			varchar(200),
  type			varchar(100),
  is_primary		char(1),
  --
  constraint fk_resource_element_site
    foreign key (site) references site (id)
    on delete cascade
);
create index ix_resource_element_site on resource_element (site);

create table pinned_releases (
  ce_id			number(10) not null,
  release		varchar(100),
  arch			varchar(100),
  --
  constraint fk_pin_resource_element
    foreign key (ce_id) references resource_element (id)
    on delete cascade
);

--insert into pinned_releases (ce_id, arch, release) values (6, 'slc4_ia32_gcc345', 'CMSSW_1_6_0');
--insert into pinned_releases (ce_id, arch, release) values (6, 'slc4_ia32_gcc345', 'CMSSW_1_2_9');

/* Site's phedex nodes */
create table phedex_node (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  site			float not null,
  name			varchar(100) not null,
  --
  constraint uk_phedex_node_name unique (id, name),
  constraint fk_phedex_node_site
    foreign key (site) references site (id)
    -- cascade?  depends on how dependant phedex becomes on this...
);
create index ix_phedex_node_site on phedex_node (site);
create index ix_phedex_node_name on phedex_node (name);



/**
 *   Site performance tables
 **/

/* High-level statistics about a site's performance */
create table performance (
  site			float not null,
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
  site			float not null,
  time			timestamp not null,
  activity		varchar(100),
  num_jobs		float,
  --
  constraint pk_job_activity primary key (site, time),
  constraint fk_job_activity_site
    foreign key (site) references site (id)
    on delete cascade
);



/**
 *  Security Module tables
 **/

/* List of cryptographic keys for the security module */
create table crypt_key (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  cryptkey		varchar(80) not null,
  time			timestamp
);
create index ix_crypt_key_cryptkey on crypt_key (cryptkey);
create index ix_crypt_key_time on crypt_key (time);



/* List of usernames and passwords for the secuirty module */
CREATE TABLE user_passwd (
  username		varchar(60) not null,
  passwd		varchar(30) not null,
  --
  constraint pk_user_passwd primary key (username)
);
create index ix_user_passwd_passwd on user_passwd (passwd);



/**
 *  "Person" definition tables
 **/

/* A human being */
create table contact (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  surname		varchar(1000) not null,
  forename		varchar(1000) not null,
  email			varchar(1000) not null,
  username		varchar(60),
  dn			varchar(1000),
  phone1		varchar(100),
  phone2		varchar(100),
  im_handle		varchar(100),
  --
  constraint uk_contact_dn unique (dn),
  constraint uk_contact_username unique (username),
  constraint fk_contact_username
    foreign key (username) references user_passwd (username)
    on delete set null
);
create index ix_contact_surname on contact (surname);
create index ix_contact_forename on contact (forename);




/**
* Management roles e.g. 'PhedexSiteAdmin', 'PhedexDataManager' 
**/
create table role (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  title			varchar(100) not null,
  --
  constraint uk_role_title unique (title)
);



/** 
 * An abstract group humans can belong to 
 * e.g. 'higgs','top','BSM','global' etc. 
 **/
create table user_group (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  name			varchar(100) not null,
  -- 
  constraint uk_user_group_name unique (name)
);



/* A mapping of humans to responsibilites associated with a site e.g. "Bob is the PhedexSiteAdmin of T4_Antartica" */
create table site_responsibility (
  contact		float not null,
  role			float not null,
  site			float not null,
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



/* A mapping of humans to responsibilities associated with a group e.g. "Joe is the ProdRequestManager of the Gravitino group */
create table group_responsibility (
  contact		float not null,
  role			float not null,
  user_group		float not null,
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
 *  Generic survey tables
 **/

/* Defines a survey and associates it with its creator */
create table survey (
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  name			varchar(100) not null,
  creator		float,
  opened		timestamp,
  closed		timestamp,
  --
  constraint fk_survey_creator
    foreign key (creator) references contact (id)
    on delete set null
);
create index ix_survery_creator on survey (creator);



/* For sending out surveys by tier */
create table survey_tiers (
  survey		float not null,
  tier			float not null,
  --
  constraint fk_survey_tiers_survey
    foreign key (survey) references survey (id)
    on delete cascade,
  constraint fk_survey_tiers_tier
    foreign key (tier) references tier (id)
    -- we don't delete tiers
);
create index ix_survey_tiers_survey on survey_tiers (survey);
create index ix_survey_tiers_tier on survey_tiers (tier);



/* For sending out surveys by role */
create table survey_roles (
  survey		float not null,
  role			float not null,
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
  id			INTEGER PRIMARY KEY AUTOINCREMENT,
  survey		float not null,
  question		varchar(4000) not null,
  form_type		varchar(100) not null,
  --
  constraint fk_question_survey
    foreign key (survey) references survey (id)
    on delete cascade
);
create index ix_question_survey on question (survey);



/* A default answer on a survey (for checkbox or drop-down menu style questions) */
create table question_default (
  question		float not null,
  pos			float not null,
  value			varchar(4000) not null,
  --
  constraint pk_question_default primary key (question, pos),
  constraint fk_question_default_question
    foreign key (question) references question (id)
    on delete cascade
);



/* A site's answer to the survey question */
create table question_answer (
  site			float not null,
  question		float not null,
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

/**
 * Quick naming convention tests
 **/

--insert into tier ( pos, name) values (0, 'Tier 0');
--insert into tier ( pos, name) values (1, 'Tier 1');
--insert into tier ( pos, name) values (2, 'Tier 2');
--insert into tier ( pos, name) values (3, 'Tier 3');
--insert into tier ( pos, name) values (4, 'Opportunistic/Other');

--insert into cms_name (name) values ('T0_CH_CERN');
--insert into cms_name (name) values ('T1_CH_CERN');
--insert into cms_name (name) values ('T1_DE_FZK');
--insert into cms_name (name) values ('T1_ES_PIC');
--insert into cms_name (name) values ('T1_FR_CCIN2P3');
--insert into cms_name (name) values ('T1_IT_CNAF');
--insert into cms_name (name) values ('T1_TW_ASGC');
--insert into cms_name (name) values ('T1_UK_RAL');
--insert into cms_name (name) values ('T1_US_FNAL');
--insert into cms_name (name) values ('T2_AT_Vienna');
--insert into cms_name (name) values ('T2_BE_IIHE');
--insert into cms_name (name) values ('T2_BE_UCL');
--insert into cms_name (name) values ('T2_BR_UERJ');
--insert into cms_name (name) values ('T2_BR_SPRACE');
--insert into cms_name (name) values ('T2_CH_CSCS');
--insert into cms_name (name) values ('T2_CN_Beijing');
--insert into cms_name (name) values ('T2_DE_DESY');
--insert into cms_name (name) values ('T2_DE_RWTH');
--insert into cms_name (name) values ('T2_EE_Estonia');
--insert into cms_name (name) values ('T2_ES_CIEMAT');
--insert into cms_name (name) values ('T2_ES_IFCA');
--insert into cms_name (name) values ('T2_FI_HIP');
--insert into cms_name (name) values ('T2_FR_CCIN2P3');
--insert into cms_name (name) values ('T2_FR_GRIF_DAPNIA');
--insert into cms_name (name) values ('T2_FR_GRIF_LAL');
--insert into cms_name (name) values ('T2_FR_GRIF_LLR');
--insert into cms_name (name) values ('T2_FR_GRIF_LPNHE');
--insert into cms_name (name) values ('T2_GR_Demokritos');
--insert into cms_name (name) values ('T2_GR_IASA');
--insert into cms_name (name) values ('T2_HU_Budapest');
--insert into cms_name (name) values ('T2_IN_TIFR');
--insert into cms_name (name) values ('T2_IT_Bari');
--insert into cms_name (name) values ('T2_IT_Legnaro');
--insert into cms_name (name) values ('T2_IT_Pisa');
--insert into cms_name (name) values ('T2_IT_Rome');
--insert into cms_name (name) values ('T2_KR_KNU');
--insert into cms_name (name) values ('T2_PL_Warsaw');
--insert into cms_name (name) values ('T2_PT_LIP_Coimbra');
--insert into cms_name (name) values ('T2_PT_LIP_Lisbon');
--insert into cms_name (name) values ('T2_RU_IHEP');
--insert into cms_name (name) values ('T2_RU_ITEP');
--insert into cms_name (name) values ('T2_RU_JINR');
--insert into cms_name (name) values ('T2_RU_PNPI');
--insert into cms_name (name) values ('T2_RU_RRC_KI');
--insert into cms_name (name) values ('T2_RU_SINP');
--insert into cms_name (name) values ('T2_TW_Taiwan');
--insert into cms_name (name) values ('T2_UK_London_Brunel');
--insert into cms_name (name) values ('T2_UK_London_Imperial');
--insert into cms_name (name) values ('T2_UK_London_QMUL');
--insert into cms_name (name) values ('T2_UK_London_RHUL');
--insert into cms_name (name) values ('T2_UK_SouthGrid_Bristol');
--insert into cms_name (name) values ('T2_UK_SouthGrid_RALPPD');
--insert into cms_name (name) values ('T2_US_Caltech');
--insert into cms_name (name) values ('T2_US_Florida');
--insert into cms_name (name) values ('T2_US_MIT');
--insert into cms_name (name) values ('T2_US_Nebraska');
--insert into cms_name (name) values ('T2_US_Purdue');
--insert into cms_name (name) values ('T2_US_UCSD');
--insert into cms_name (name) values ('T2_US_Wisconsin');
--insert into cms_name (name) values ('T3_DE_Karlsruhe');
--insert into cms_name (name) values ('T3_FR_IN2P3_IPNL');
--insert into cms_name (name) values ('T3_FR_IRES');
--insert into cms_name (name) values ('T3_IT_Napoli');
--insert into cms_name (name) values ('T3_IT_Perugia');
--insert into cms_name (name) values ('T3_IT_Trieste');
--insert into cms_name (name) values ('T3_US_Minnesota');
--insert into cms_name (name) values ('T3_US_Princeton');
--insert into cms_name (name) values ('T3_US_TTU');
--insert into cms_name (name) values ('T3_US_UCLA');
--insert into cms_name (name) values ('T3_US_UCR');
--insert into cms_name (name) values ('T3_US_UIowa');
--insert into cms_name (name) values ('T3_US_Vanderbilt');

--insert into sam_name (name) values ("UKI-LT2-Brunel");
--insert into sam_name (name) values ("UKI-LT2-IC-HEP");
--insert into sam_name (name) values ("UKI-LT2-RHUL");
--insert into sam_name (name) values ("UKI-LT2-IC-LeSC");
--insert into sam_name (name) values ("RAL-LCG2");
--insert into sam_name (name) values ("USCMS-FNAL-WC1");

/*select * from sam_name;*/

--insert into phedex_node (site, name) values(1, "T2_London_Brunel");
--insert into phedex_node (site, name) values(1, "T2_London_IC");
--insert into phedex_node (site, name) values(1, "T2_London_RHUL");

--insert into site (name, tier, country) values ("London", 3, "UK");
--insert into site ( gocdbid, name, tier, country, usage, url, logourl) 
--          values (1, 'RAL', 2, 'the UK', 'LCG', 'https://twiki.cern.ch/twiki/bin/view/CMS/RutherfordLabs', 'http://www.cclrc.ac.uk/img/CCLRC300.jpg');
--insert into site ( gocdbid, name, tier, country, usage, url) 
--          values (51, 'RAL PPD', 3, 'the UK', 'LCG', 'https://twiki.cern.ch/twiki/bin/view/CMS/RutherfordLabs');
--insert into site ( gocdbid, name, tier, country, usage, url) 
--          values (27, 'Brightlingsea', 4, 'the UK', 'LCG', 'https://twiki.cern.ch/twiki/bin/view/CMS/RutherfordLabs');
--insert into site ( gocdbid, name, tier, country, usage, url, logourl) 
--          values (16, 'FNAL', 2, 'the USA', 'OSG', 'http://www.fnal.gov', 'http://lss.fnal.gov/orientation/pictures/orangelogo.gif');
/*select * from site;*/

--insert into resource_element (site, fqdn, type) values (1, "ce00.hep.ph.ic.ac.uk", "CE");
--insert into resource_element (site, fqdn, type) values (1, "mars-ce2.mars.lesc.doc.ic.ac.uk", "CE");
--insert into resource_element (site, fqdn, type) values (1, "dgc-grid-40.brunel.ac.uk", "CE");
--insert into resource_element (site, fqdn, type) values (1, "dgc-grid-35.brunel.ac.uk", "CE");
--insert into resource_element (site, fqdn, type) values (1, "ce1.pp.rhul.ac.uk", "CE");
/*select * from resource_element;*/

--insert into site_cms_name_map (site_id, cms_name_id) values (1, 47);
--insert into site_cms_name_map (site_id, cms_name_id) values (1, 48);
--insert into site_cms_name_map (site_id, cms_name_id) values (1, 49);
--insert into site_cms_name_map (site_id, cms_name_id) values (1, 50);
--insert into site_cms_name_map (site_id, cms_name_id) values (8, 5);
--insert into site_cms_name_map (site_id, cms_name_id) values (9, 6);
/*select * from site_cms_name_map;*/

--insert into resource_cms_name_map (resource_id, cms_name_id) values (1, 1);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (2, 1);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (3, 1);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (4, 1);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (5, 1);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (2, 1);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (3, 3);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (4, 3);
--insert into resource_cms_name_map (resource_id, cms_name_id) values (5, 4);
/*select * from resource_cms_name_map;*/

--insert into sam_cms_name_map (sam_id, cms_name_id) values (1, 1);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (2, 1);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (3, 1);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (4, 1);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (2, 2);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (1, 3);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (3, 4);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (4, 2);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (5, 5);
--insert into sam_cms_name_map (sam_id, cms_name_id) values (6, 6);
/*select * from sam_cms_name_map;*/


--insert into site_association (parent_site, child_site) values (1, 2);
--insert into phedex_node ( site, name) values (2, 'T1_RAL_Buffer');
      
--insert into user_group (name) values('global');
          
--insert into contact ( surname, forename, email, dn, phone1, username, im_handle)
--          values('admin', 'admin', 'hn-cms-webInterfaces@cern.ch', 'n=admin', '0123456789', 'admin', 'aol:simonmetson1234');

--insert into contact ( surname, forename, email, dn, phone1, username, im_handle)
--          values('fred', 'blogs', 'hn-cms-webInterfaces@cern.ch', 'n=fred', '0123456789', 'fred', 'msn:superted_79@hotmail.com');

--insert into crypt_key ( cryptkey) VALUES ('T05FIGVmZ2hpamtsbW5vcHFyc3R1dnd4eXphYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5emFiZGU=');
--insert into user_passwd (username, passwd) values('admin', 'forh75ZkVhdTU');      
--insert into role ( title) values('Site Admin');
--insert into role ( title) values('Site Executive');
--insert into role ( title) values('PhEDEx Contact');
--insert into role ( title) values('Data Manager');
--insert into role ( title) values('Global Admin');

--insert into site_responsibility(contact, site, role) values(1, 2, 1);
--insert into site_responsibility(contact, site, role) values(1, 2, 3);
--insert into site_responsibility(contact, site, role) values(2, 2, 2);
--insert into site_responsibility(contact, site, role) values(2, 1, 5);
--insert into site_responsibility(contact, site, role) values(2, 1, 1);
--insert into site_responsibility(contact, site, role) values(3, 1, 3);
--insert into site_responsibility(contact, site, role) values(4, 1, 2);
--insert into group_responsibility(contact, user_group, role) values(1, 1, 1);
--insert into group_responsibility(contact, user_group, role) values(2, 1, 1);
--insert into group_responsibility(contact, user_group, role) values(4, 1, 1);
--insert into resource_element ( site, fqdn, type, is_primary) values(2, 'lcgce01.gridpp.rl.ac.uk', 'CE', 'y');
--insert into resource_element ( site, fqdn, type, is_primary) values(2, 'ralsrma.rl.ac.uk', 'SE', 'y');
--insert into resource_element ( site, fqdn, type, is_primary) values(2, 'dcache.gridpp.rl.ac.uk', 'SE', 'n');
--insert into resource_element ( site, fqdn, type, is_primary) values(3, 'heplnx206.pp.rl.ac.uk', 'CE', 'n');
--insert into resource_element ( site, fqdn, type, is_primary) values(3, 'heplnx201.pp.rl.ac.uk', 'CE', 'y');      
--insert into resource_element ( site, fqdn, type, is_primary) values(3, 'heplnx204.pp.rl.ac.uk', 'SE', 'y');

/* Get the CMS name for a site */
/* select cms_name.name,  site.name from site*/
/* 	join site_cms_name_map on site_cms_name_map.site_id = site.id*/
/* 	join cms_name on cms_name.id = site_cms_name_map.cms_name_id*/
/* 	where site.id = 1;*/
/*
select site.id, site.name, tier.name from site 
  join tier on tier.id = site.tier
  order by site.tier, site.name;
*/
select site.name, sam_name.name, cms_name.name, tier.name from site 
  join tier on tier.id = site.tier
  join site_cms_name_map on site_cms_name_map.site_id = site.id
  join cms_name on cms_name.id = site_cms_name_map.cms_name_id
  join sam_cms_name_map on sam_cms_name_map.cms_name_id = site_cms_name_map.cms_name_id
  join sam_name on sam_name.id = sam_cms_name_map.sam_id
  order by site.tier, cms_name.name;
/*
select site.id, sam_name.name, tier.name from site 
  join tier on tier.id = site.tier
  join site_cms_name_map on site_cms_name_map.site_id = site.id
  join sam_cms_name_map on sam_cms_name_map.cms_name_id = site_cms_name_map.cms_name_id
  join sam_name on sam_name.id = sam_cms_name_map.sam_id
  order by site.tier, sam_name.name;
*/
select site.id, phedex_node.name, tier.name from site 
  join tier on tier.id = site.tier
  join phedex_node on phedex_node.site = site.id
  order by site.tier, phedex_node.name;
/*
select site.id, resource_element.fqdn, tier.name from site 
  join tier on tier.id = site.tier
  join resource_element on resource_element.site = site.id
  where resource_element.type = "CE"
  order by site.tier, resource_element.fqdn;

select site.id, resource_element.fqdn, tier.name from site 
  join tier on tier.id = site.tier
  join resource_element on resource_element.site = site.id
  where resource_element.type = "SE"
  order by site.tier, resource_element.fqdn;

/* get the sam name, and the CMS name for a site 
 * select sam_name.id, sam_name.name, cms_name.name, site.name from site
 * 	join site_cms_name_map on site_cms_name_map.site_id = site.id
 * 	join cms_name on cms_name.id = site_cms_name_map.cms_name_id
 * 	join sam_cms_name_map on sam_cms_name_map.cms_name_id = site_cms_name_map.cms_name_id
 * 	join sam_name on sam_name.id = sam_cms_name_map.sam_id	
 * 	where site.id = 1;	
*/
/* get the sam name, and the cms name by resource element 
 * select sam_cms_name_map.sam_id, sam_name.name, resource_cms_name_map.cms_name_id, cms_name.name, resource_element.id, resource_element.fqdn from resource_element
 * 	join resource_cms_name_map on resource_cms_name_map.resource_id = resource_element.id
 * 	join cms_name on cms_name.id = resource_cms_name_map.resource_id
 * 	join sam_cms_name_map on sam_cms_name_map.cms_name_id = resource_cms_name_map.cms_name_id
 * 	join sam_name on sam_name.id = sam_cms_name_map.sam_id;
*/