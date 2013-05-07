/**
 *  Set of parameters passed via web 
 *  Type of sensor 		(eg. RATE)
 *  User ID			(eg. 111) -> comes from SiteDB
 *  Sensor parameter		(to_node=T1_CERN_Buffer,from_node=T1_FNAL_Buffer)
 *  Alarm threshold 		(<10MB/s)
 *  Alert			(eg. RATE<10MB/S=ON)		
 *
 *  Ps.: In order to a client to have an alert using a combination of alarms
 *  the client has to have more than one sensor to use a combination like
 *  Alarm_1 = ON AND Alarm_2 = ON OR Alarm_3 = ON
 *
 **/

/**
 *
 *  "Sensor" definition table
 *  ---------------------------
 *  A sensor has an unique name.
 *  
 *  Example: 
 *  name='RATE'			<-pre-defined but still comes via web
 *  name='QUALITY'		 
 *  name='PROXY'
 *  name='AGENT'
 *
 **/

create table sensor (
	sensor_id		number(10) not null,
	name			varchar(100) not null,
	--
	constraint pk_sensor primary key (sensor_id),
	constraint uk_name unique (name)
);
create sequence sensor_sq increment by 1 start with 1;


/**
 *
 *  "User Sensor" definition table
 *  ---------------------------
 *  A client has a sensor running. This client has an id 
 *  and an alert (combination of alarms).
 *
 *  Example:
 *  sensor_id=1		(RATE) 						<-set via web
 *  user_id=1		(Jonh)						<-set via web
 *  parameters=	{to_node=T1_CERN_Buffer,				<-set via web
 *			 from_node=T1_FNAL_Buffer,
 *			 sample_time*=10}				*sample_time in hours
 *
 **/

create table user_sensor (
	user_sensor_id			number(10) not null,
	sensor_id			number(10) not null,
	user_id				number(10) not null,
	parameters			varchar2(1000),
	description			varchar(1000) not null,
	script				varchar(1000) not null,
	--
	constraint pk_user_sensor primary key (user_sensor_id),
	constraint fk_sensor foreign key (sensor_id) references sensor (sensor_id),
	constraint uk_user_sensor unique (sensor_id,user_id,parameters,script)
);
create sequence user_sensor_sq increment by 1 start with 1;


/**
 *  
 *  "Operators" definition table
 *  ---------------------------
 *  
 *  Maps a number to an operation.
 * 
 *  Definition: 
 *    id  	meaning			<-pre-defined 
 *    0		=
 *    1		<
 *    2		>
 *    3		!=
 *    4		<=
 *    5		>=
 *    
 **/

create table operator (
	operator_id		number(10) not null,
	value			varchar(10) not null,
	--
	constraint pk_operator primary key (operator_id),
	constraint uk_operator unique (value)
);
create sequence operator_sq increment by 1 start with 1;


/**
 *  
 *  "Alarms" definition table
 *  ---------------------------
 *  
 *  An alarm is defined by the client and is related to the sensor.
 *  It has a threshold and a operator
 *  
 *  Example: 
 *  client_sensor_id=1		(RATE,Jonh,T1_FNAL_Buffer->T1_CERN_Buffer in the last 10 hours)
 *  threshold=10		(10MB/s) 			<-passed via web
 *  operator='1'		('<')				<-passed via web
 *  
 **/

create table alarm (
	alarm_id			number(10) not null,
	user_sensor_id		number(10) not null,
	threshold			number(10) not null,
	operator_id			number(10) not null,
	--
	constraint pk_alarm primary key (alarm_id),
	constraint fk_operator foreign key (operator_id) references operator (operator_id),
	constraint fk_user_sensor foreign key (user_sensor_id) references user_sensor (user_sensor_id),
	constraint uk_alarm unique (user_sensor_id,threshold,operator_id)
);
create sequence alarm_sq increment by 1 start with 1;


/**
 *  
 *  "Alert" definition table
 *  ---------------------------
 *
 *  User defined combination of alarms (which can be just a simple alarm).  
 *
 *  Example: 
 *  user_id=1			get from SiteDB	(name='Jonh',contact_method='SMS',contact_value='0227676767')
 *  combination='A1||A2&&A3'			<-passed via web but it is a "composed" alarm foreign key
 *  
 *  
 *  For first iteration combination == alarm_id
 *  Second (third?) iteration is list of alarm_id and operators between them
 *  
 *  Problem is how we enter the alert list from web GUI, not how they are evaluated
 *  
 **/

create table alert (
	alert_id			number(10) not null,
	user_id				number(10) not null,
	combination			varchar(100) not null,
	actuator			varchar(1000),
	--
	constraint pk_alert primary key (alert_id),
	constraint uk_alert unique (user_id, combination)
);
create sequence alert_sq increment by 1 start with 1;
