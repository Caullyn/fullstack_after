BEGIN;

    SELECT session_id
      FROM abuser.usp_abuser_add_update('ex@mple.com','asdfasdf',1::BIGINT);

COMMIT;

select * from abuser.abuser;    
