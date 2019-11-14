create schema if not exists dbf79d1040d58c4b2da431a88d017b1284 collate latin1_swedish_ci;

create table if not exists auth_group
(
	id int auto_increment
		primary key,
	name varchar(150) null
)
charset=utf8mb4;

create table if not exists auth_user
(
	id int auto_increment,
	password varchar(128) null,
	last_login datetime null,
	is_superuser tinyint(1) null,
	username varchar(150) null,
	email varchar(254) null,
	first_name varchar(20) null,
	last_name varchar(150) null,
	is_staff tinyint(1) null,
	is_active tinyint(1) null,
	date_joined datetime null,
	constraint auth_user_id_uindex
		unique (id),
	constraint auth_user_username_uindex
		unique (username)
)
charset=utf8mb4;

alter table auth_user
	add primary key (id);

create table if not exists auth_user_groups
(
	id int auto_increment
		primary key,
	user_id int null,
	group_id int null,
	constraint auth_user_groups_constraint
		unique (user_id, group_id),
	constraint auth_user_groups_auth_group_id_fk
		foreign key (group_id) references auth_group (id),
	constraint auth_user_groups_auth_user_id_fk
		foreign key (user_id) references auth_user (id)
)
charset=utf8mb4;

create table if not exists authtoken_token
(
	`key` varchar(40) null,
	created datetime null,
	user_id int null,
	constraint authtoken_token_uniq
		unique (`key`),
	constraint authtoken_token_uniq2
		unique (user_id),
	constraint authtoken_token_auth_user_id_fk
		foreign key (user_id) references auth_user (id)
)
charset=utf8mb4;

create table if not exists django_content_type
(
	id int auto_increment
		primary key,
	app_label varchar(100) null,
	model varchar(100) null
)
charset=utf8mb4;

create table if not exists auth_permission
(
	id int auto_increment
		primary key,
	content_type_id int null,
	codename varchar(100) null,
	name varchar(255) null,
	constraint auth_permission_django_content_type_id_fk
		foreign key (content_type_id) references django_content_type (id)
)
charset=utf8mb4;

create table if not exists auth_group_permissions
(
	id int auto_increment
		primary key,
	group_id int not null,
	permission_id int not null,
	constraint auth_group_permissions_auth_group_id_fk
		foreign key (group_id) references auth_group (id),
	constraint auth_group_permissions_auth_permission_id_fk
		foreign key (permission_id) references auth_permission (id)
)
charset=utf8mb4;

create table if not exists auth_user_user_permissions
(
	id int auto_increment
		primary key,
	user_id int null,
	permission_id int null,
	constraint auth_user_user_permissions_uniq
		unique (user_id, permission_id),
	constraint auth_user_user_permissions_auth_permission_id_fk
		foreign key (permission_id) references auth_permission (id),
	constraint auth_user_user_permissions_auth_user_id_fk
		foreign key (user_id) references auth_user (id)
)
charset=utf8mb4;

create table if not exists django_admin_log
(
	id int auto_increment
		primary key,
	action_time datetime null,
	object_id text null,
	object_repr varchar(200) null,
	change_message text null,
	content_type_id int null,
	user_id int null,
	action_flag smallint null,
	constraint django_admin_log_auth_user_id_fk
		foreign key (user_id) references auth_user (id),
	constraint django_admin_log_django_content_type_id_fk
		foreign key (content_type_id) references django_content_type (id)
)
charset=utf8mb4;

create table if not exists django_migrations
(
	id int null,
	app varchar(255) null,
	name varchar(255) null,
	applied datetime null
)
charset=utf8mb4;

create table if not exists django_session
(
	session_key varchar(40) null,
	session_data text null,
	expire_date datetime null,
	constraint django_session_session_key_uindex
		unique (session_key)
)
charset=utf8mb4;

create table if not exists question_option_type
(
	q_opt_typ_cd varchar(255) default '' not null
		primary key,
	q_opt_nm varchar(255) null,
	void_ind varchar(1) default 'n' null
);

create table if not exists question_options
(
	q_opt_id int auto_increment
		primary key,
	q_opt_typ_cd varchar(255) null,
	`option` varchar(255) not null,
	void_ind varchar(1) default 'n' null,
	constraint question_options_question_option_type_q_opt_typ_cd_fk
		foreign key (q_opt_typ_cd) references question_option_type (q_opt_typ_cd)
);

create table if not exists question_type
(
	question_typ varchar(50) not null
		primary key,
	question_typ_nm varchar(255) not null,
	void_ind varchar(1) default 'n' not null
);

create table if not exists role
(
	role_id bigint not null
		primary key,
	role_nm varchar(50) not null
);

create table if not exists season
(
	season_id int auto_increment
		primary key,
	season varchar(45) not null
);

create table if not exists event
(
	event_id int auto_increment
		primary key,
	season_id int null,
	event_nm varchar(255) not null,
	date_st datetime not null,
	event_cd varchar(10) not null,
	date_end datetime not null,
	void_ind varchar(1) default 'n' null,
	constraint event_event_cd_uindex
		unique (event_cd),
	constraint event___fk_season
		foreign key (season_id) references season (season_id)
);

create table if not exists scout_field_question
(
	sfq_id int auto_increment
		primary key,
	season_id int not null,
	question_typ varchar(50) not null,
	q_opt_typ_cd varchar(255) null,
	question varchar(1000) not null,
	`order` int default 0 not null,
	void_ind varchar(1) default 'n' not null,
	constraint fk_sfq_question_type
		foreign key (question_typ) references question_type (question_typ),
	constraint fk_sfq_season
		foreign key (season_id) references season (season_id),
	constraint scout_field_question_question_option_type_q_opt_typ_cd_fk
		foreign key (q_opt_typ_cd) references question_option_type (q_opt_typ_cd)
);

create table if not exists scout_pit_question
(
	spq_id int not null
		primary key,
	season_id int not null,
	question_typ varchar(50) null,
	q_opt_typ_cd varchar(255) null,
	question varchar(1000) not null,
	void_ind varchar(1) default 'n' not null,
	constraint fk_spq_question_type
		foreign key (question_typ) references question_type (question_typ),
	constraint fq_spq_season
		foreign key (season_id) references season (season_id),
	constraint scout_pit_question_question_option_type_q_opt_typ_cd_fk
		foreign key (q_opt_typ_cd) references question_option_type (q_opt_typ_cd)
);

create table if not exists team
(
	team_no int not null
		primary key,
	team_nm varchar(255) not null,
	void_ind varchar(1) default 'n' null
);

create table if not exists event_team_xref
(
	event_id int not null,
	team_no int not null,
	primary key (event_id, team_no),
	constraint event_team_xref_fk0
		foreign key (event_id) references event (event_id),
	constraint event_team_xref_fk1
		foreign key (team_no) references team (team_no)
);

create table if not exists pit
(
	pit_id bigint auto_increment
		primary key,
	event_id int null,
	team_no int not null,
	drivetrain varchar(500) not null,
	speed varchar(50) not null,
	fabrication varchar(50) not null,
	rocket varchar(500) not null,
	auto varchar(5000) not null,
	teleop varchar(5000) not null,
	cargo_ship varchar(5000) not null,
	ball_mech varchar(500) not null,
	climb varchar(2000) null,
	strategy varchar(5000) null,
	hatch_mech varchar(500) null,
	img_id varchar(500) null,
	img_ver varchar(500) null,
	constraint fk_0
		foreign key (event_id) references event (event_id),
	constraint fk_1
		foreign key (team_no) references team (team_no)
);

create table if not exists robot_match
(
	match_id int auto_increment
		primary key,
	event_id int not null,
	team_no int not null,
	sandstorm varchar(1) null,
	st_lvl int null,
	pre_cargo_hp int null,
	pre_cargo_c int null,
	pre_rocket_hp int null,
	pre_rocket_c int null,
	auto_cargo_hp int null,
	auto_cargo_c int null,
	auto_rocket_hp int null,
	auto_rocket_c int null,
	teleop_cargo_hp int null,
	teleop_cargo_c int null,
	teleop_rocket_hp int null,
	teleop_rocket_c int null,
	lv_climb int null,
	comments varchar(5000) null,
	constraint robot_match_ibfk_1
		foreign key (event_id) references event (event_id),
	constraint robot_match_ibfk_2
		foreign key (team_no) references team (team_no)
);

create index event_id
	on robot_match (event_id);

create index team_no
	on robot_match (team_no);

create table if not exists scout_field
(
	scout_field_id int auto_increment
		primary key,
	event_id int not null,
	team_no int not null,
	void_ind varchar(1) default 'n' not null,
	constraint fk_scout_field_event
		foreign key (event_id) references event (event_id),
	constraint fk_scout_field_team
		foreign key (team_no) references team (team_no)
);

create table if not exists scout_field_answer
(
	sfa_id int auto_increment
		primary key,
	scout_field_id int not null,
	sfq_id int not null,
	answer varchar(1000) null,
	void_ind varchar(1) default 'n' not null,
	constraint fk_sfa_sfq
		foreign key (sfq_id) references scout_field_question (sfq_id),
	constraint fk_sfq_scout_field
		foreign key (scout_field_id) references scout_field (scout_field_id)
);

create table if not exists scout_pit
(
	scout_pit_id int auto_increment
		primary key,
	event_id int not null,
	team_no int not null,
	img_id varchar(500) null,
	img_ver varchar(500) null,
	void_ind varchar(1) default 'n' not null,
	constraint fk_scout_pit_event
		foreign key (event_id) references event (event_id),
	constraint fk_scout_pit_team
		foreign key (team_no) references team (team_no)
);

create table if not exists scout_pit_answer
(
	spa_id int auto_increment
		primary key,
	scout_pit_id int not null,
	spq_id int not null,
	answer varchar(1000) null,
	void_ind varchar(1) default 'n' not null,
	constraint fk_spa_scout_pit
		foreign key (scout_pit_id) references scout_pit (scout_pit_id),
	constraint fk_spa_spq
		foreign key (spq_id) references scout_pit_question (spq_id)
);

create table if not exists user
(
	user_id bigint auto_increment
		primary key,
	username varchar(50) not null,
	password varchar(255) not null,
	email varchar(255) not null,
	confirmed_at datetime null,
	active tinyint(1) not null,
	first_name varchar(100) not null,
	last_name varchar(100) not null
);

create table if not exists user_links
(
	user_links_id int auto_increment
		primary key,
	permission_id int not null,
	menu_name varchar(255) not null,
	routerlink varchar(255) not null,
	constraint user_links_auth_permission_id_fk
		foreign key (permission_id) references auth_permission (id)
);

create table if not exists user_roles
(
	user_role_id bigint auto_increment
		primary key,
	user_id bigint not null,
	role_id bigint not null,
	constraint user_roles_ibfk_1
		foreign key (user_id) references user (user_id),
	constraint user_roles_ibfk_2
		foreign key (role_id) references role (role_id)
);

create index role_id
	on user_roles (role_id);

create index user_id
	on user_roles (user_id);

