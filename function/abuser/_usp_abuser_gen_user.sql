CREATE OR REPLACE FUNCTION abuser._usp_abuser_gen_user()
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    _user BIGINT;
BEGIN

    _user = ((EXTRACT(epoch from now()) * 100000)::TEXT || 100::TEXT)::BIGINT;
    RETURN _user;
    
END;
$$;