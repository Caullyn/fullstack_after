CREATE OR REPLACE FUNCTION event.usp_event_display(
    i_evt_id BIGINT,
    i_asr_geo_id BIGINT,
    i_band TEXT
)
RETURNS TABLE(
    evt_id BIGINT,
    evt_name TEXT,
    evt_description TEXT,
    evt_start TEXT,
    evt_end TEXT,
    status_id INT,
    status_desc TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    _status_id INT;
    _status_desc TEXT;
BEGIN

    _status_id = 200;
    _status_desc = 'events returned: 15';
    IF i_evt_id IS NOT NULL THEN        
        RETURN QUERY 
        SELECT evt.evt_id, evt.evt_name, evt.evt_description, 
               to_char(evt.evt_start, 'Mon DD HH:MI'), to_char(evt.evt_end, 'Mon DD HH:MI'),
               _status_id, _status_desc
          FROM event.event evt
         WHERE evt.evt_id = i_evt_id;
    ELSE
        RETURN QUERY 
        SELECT evt.evt_id, evt.evt_name, evt.evt_description, 
               to_char(evt.evt_start, 'Mon DD HH:MI'), to_char(evt.evt_end, 'Mon DD HH:MI'),
               _status_id, _status_desc
          FROM event.event evt
         WHERE (evt.evt_start > now() OR evt.evt_end > now())
         ORDER BY evt.evt_start DESC, evt_name
         LIMIT 15;
    END IF;
END;
$$;