CREATE TABLE auth_n_user (
     id INTEGER AUTO_INCREMENT PRIMARY KEY,
     dn VARCHAR(512),
     username VARCHAR(60) UNIQUE
);
CREATE TABLE auth_z_scope (
     id INTEGER AUTO_INCREMENT PRIMARY KEY,
     scope VARCHAR(60) NOT NULL UNIQUE
);
CREATE TABLE auth_z_role (
     id INTEGER AUTO_INCREMENT PRIMARY KEY,
     role VARCHAR(60) NOT NULL UNIQUE
);
CREATE TABLE auth_z_user_role (
     user_id INT,
     role_id INT,
     scope_id INT
);
CREATE TABLE crypt_key (
     id INTEGER AUTO_INCREMENT PRIMARY KEY,
     cryptkey VARBINARY(56) NOT NULL,
     time TIMESTAMP
);
CREATE TABLE user_passwd (
     username VARCHAR(60) UNIQUE,
     description VARCHAR(60),
     passwd VARCHAR(30)
);

