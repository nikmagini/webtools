/* List of cryptographic keys for the security module */
create table crypt_key (
  id			number(10) not null,
  cryptkey		varchar(80) not null,
  time			timestamp,
  --
  constraint pk_crypt_key primary key (id)
);
create sequence crypt_key_sq increment by 1 start with 1;
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



/* A human being */
create table contact (
  id			number(10) not null,
  username		varchar(60),
  dn			varchar(1000),
  --
  constraint pk_contact primary key (id),
  constraint uk_contact_dn unique (dn),
  constraint uk_contact_username unique (username),
  constraint fk_contact_username
    foreign key (username) references user_passwd (username)
    on delete set null
);
create sequence contact_sq increment by 1 start with 1;



/* Management roles e.g. 'PhedexSiteAdmin', 'PhedexDataManager' */
create table role (
  id			number(10) not null,
  title			varchar(100) not null,
  --
  constraint pk_role primary key (id),
  constraint uk_role_title unique (title)
);
create sequence role_sq increment by 1 start with 1;



/* Site definition and associated data */
create table site (
  id			number(10) not null,
  name			varchar(100) not null,
  --
  constraint pk_site primary key (id),
  constraint uk_site unique (name)
);
create sequence site_sq increment by 1 start with 1;



/* An abstract group humans can belong to 
   e.g. 'higgs','top','BSM','global' etc. */
create table user_group (
  id			number(10) not null,
  name			varchar(100) not null,
  --
  constraint pk_user_group primary key (id), 
  constraint uk_user_group_name unique (name)
);
create sequence user_group_sq increment by 1 start with 1;



/* A mapping of humans to responsibilites associated with a site 
   e.g. "Bob is the PhedexSiteAdmin of T4_Antartica" */
create table site_responsibility (
  contact		number(10) not null,
  role			number(10) not null,
  site			number(10) not null,
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
  contact		number(10) not null,
  role			number(10) not null,
  user_group		number(10) not null,
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
