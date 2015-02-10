CREATE OR REPLACE FUNCTION sess.usp_sess_add(
    i_asr_user BIGINT
)
RETURNS TABLE(
    sess_id TEXT,
    status_id INT,
    status_desc TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _sess TEXT;
BEGIN
 
    SELECT 
     regexp_replace(
       encode(
         gen_random_bytes(6), 'base64'),
         '[/=+]',
         'l', 'g'
       )::TEXT 
    INTO _sess;
    
    INSERT INTO sess.session (ses_user, ses_session)
    SELECT i_asr_user, _sess;        
    
    RETURN QUERY SELECT _sess, 200, 'OK'::TEXT;
    
END;
$$;