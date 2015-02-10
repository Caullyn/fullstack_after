CREATE OR REPLACE FUNCTION sess.usp_sess_check(
    i_sess TEXT
)
RETURNS TABLE(
    asr_user BIGINT,
    status_id INT,
    status_desc TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _user BIGINT;
    _sess TEXT;
    _ses_id BIGINT;
    _status_id INT;
    _status_desc TEXT;
BEGIN
    
    SELECT a[1], a[2]
      INTO _user, _sess
      FROM (
            SELECT regexp_split_to_array(i_sess, ',')
        ) AS dt(a);
        
    SELECT ses_id
      INTO _ses_id
      FROM sess.session
     WHERE ses_user = _user
       AND ses_session = _sess
       AND NOT ses_expired;
    
    IF _ses_id > 0 THEN
        _status_id = 200;
        _status_desc = 'OK.';
    ELSE
        _status_id = 400;
        _status_desc = 'No active token.';
    END IF;
    
    RETURN QUERY SELECT _user, _status_id, _status_desc;
    
END;
$$;