use users;

create or replace table users(
	user_id				int 			NOT NULL AUTO_INCREMENT PRIMARY KEY,
	user_uuid			varchar(240),
	username			varchar(240),
	password			varchar(240),
	email_address		varchar(240),
	first_name			varchar(240),
	middle_name			varchar(240),
	last_name			varchar(240),
	creation_date		datetime,
	last_update_date 	datetime,
	attribute1			varchar(150),
	attribute2			varchar(150),
	attribute3			varchar(150),
	attribute4			varchar(150),
	attribute5			varchar(150)
);