/**
 *  A minimal set of tables containing only what concerns the security module
 *
 **/


/* List of cryptographic keys for the security module */
create table crypt_key (
  id			INTEGER not null PRIMARY KEY AUTOINCREMENT,
  cryptkey		varchar(80) not null,
  time			timestamp
);
create index ix_crypt_key_cryptkey on crypt_key (cryptkey);
create index ix_crypt_key_time on crypt_key (time);



/* List of usernames and passwords for the secuirty module */
CREATE TABLE user_passwd (
  username		varchar(60) not null,
  description           varchar(100),
  passwd		varchar(30) not null,
  --
  constraint pk_user_passwd primary key (username)
);
create index ix_user_passwd_passwd on user_passwd (passwd);



/* A human being */
create table contact (
  id			INTEGER not null PRIMARY KEY AUTOINCREMENT,
  username		varchar(60) not null,
  surname               varchar(1000) not null,
  forename              varchar(1000) not null,
  email                 varchar(1000) not null,

  dn			varchar(1000),
  --
  constraint uk_contact_dn unique (dn)
);



/* Management roles e.g. 'PhedexSiteAdmin', 'PhedexDataManager' */
create table role (
  id			INTEGER  not null PRIMARY KEY AUTOINCREMENT,
  title			varchar(100) not null,
  --
  constraint uk_role_title unique (title)
);



/* An abstract group humans can belong to 
   e.g. 'higgs','top','BSM','global' etc. */
create table user_group (
  id			INTEGER not null PRIMARY KEY AUTOINCREMENT,
  name			varchar(100) not null,
  --
  constraint uk_user_group_name unique (name)
);



/* Site definition */
create table site (
  id			INTEGER not null PRIMARY KEY  AUTOINCREMENT,
  name			varchar(100) not null,
  tier                  number(10) not null,
  country               varchar(100) not null,

  --
  constraint uk_site unique (name)
);



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
