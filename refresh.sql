update user_user 
set password = 'null',
email = id || 'test@bduke.dev',
last_name = 'test',
discord_user_id = NULL ,
phone = null
where id not in (-1, 1);

update alerts_channelsend  SET dismissed_time = SYSDATE() where dismissed_time  is null
and comm_typ_id  = 'notification';

select * from alerts_channelsend
where dismissed_time  is null
and comm_typ_id  = 'notification';