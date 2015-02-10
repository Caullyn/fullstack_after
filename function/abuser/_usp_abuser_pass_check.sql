CREATE OR REPLACE FUNCTION abuser._usp_abuser_pass_check(
    i_email TEXT,
    i_pass TEXT
)
RETURNS TABLE(
    session_id TEXT,
    status_id INT,
    status_desc TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _salt TEXT;
    _pass TEXT;
    _user BIGINT;
    _sess TEXT;
    _status_id INT;
    _status_desc TEXT;
    _auth bytea;
BEGIN

    SELECT asr.asr_user, sal_salt, asr_password
      INTO _user, _salt, _pass
      FROM abuser.salt sal
      JOIN abuser.abuser asr ON asr.asr_geo_id = sal.sal_geo_id
     WHERE asr.asr_email = i_email;
    
    _auth = digest(_salt||i_pass||i_email::text, 'sha256');
    
    IF _auth::text = _pass THEN
        _status_id = 200;
        _status_desc = 'Abuser Authenticated.';
        SELECT _user || ',' || sess_id
          INTO _sess
          FROM sess.usp_sess_add(_user);
    ELSE
        _status_id = 400;
        _status_desc = 'Abuser Authentication Failed.';
    END IF;    
    
    RETURN QUERY SELECT _sess, _status_id, _status_desc;
END;
$$;