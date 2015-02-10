CREATE OR REPLACE FUNCTION abuser._usp_abuser_pass_add(
    i_email TEXT,
    i_geo_id BIGINT,
    i_pass TEXT
)
RETURNS TABLE(
    pass TEXT,
    status_id INT,
    status_desc TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _salt TEXT;
    _pass TEXT;
    _status_id INT;
    _status_desc TEXT;
    _auth TEXT;
BEGIN

    IF length(i_pass) > 5 THEN
    
        SELECT sal_salt
          INTO _salt
          FROM abuser.salt sal
         WHERE sal.sal_geo_id = i_geo_id;
        IF _salt IS NOT NULL THEN
            _auth = digest(_salt||i_pass||i_email::text, 'sha256');
            _status_id = 200;
            _status_desc = 'Abuser Authenticated.';
        ELSE
            _status_id = 400;
            _status_desc = 'Abuser Salt or Geo Location Does Not Exist.';
        END IF;
    ELSE
        _status_id = 401;
        _status_desc = 'Abuser Password Too Short.';
    END IF;    
    
    RETURN QUERY SELECT _auth, _status_id, _status_desc;
END;
$$;