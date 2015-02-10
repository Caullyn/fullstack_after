do
$d$
declare
    _sess TEXT;
BEGIN

    SELECT min(asr_user)    
      INTO _sess
      FROM abuser.abuser;
          
    PERFORM  band.usp_band_add_update(
        _sess,
        'wotjam ample sample example',
        'wase@gmail.com',
        'Just a band example.',
        1); 

    PERFORM  event.usp_event_add_update(
        _sess,
        'Pre-show jam'::TEXT,
        'An intimate jam to get ready for our big show.'::TEXT,
        (now() + '1 week'::interval)::TIMESTAMPTZ,
        (now() + '1 week'::interval + '3 hours'::interval)::TIMESTAMPTZ,
        NULL::BIGINT,
        1::BIGINT,
        '{}',
        '1',
        '1',
        -5::NUMERIC(20,17),
        100::NUMERIC(20,17),
        'place'::TEXT);
        
    PERFORM  event.usp_event_add_update(
        _sess,
        'The big show',
        'Our big show.',
        now() + '8 days'::interval,
        now() + '8 days'::interval + '3 hours'::interval,
        NULL,
        1,
        '{}',
        '1',
        '1',
        -5::NUMERIC(20,17),
        100::NUMERIC(20,17),
        'place'::TEXT);
        
    PERFORM  event.usp_event_add_update(
        _sess,
        'Post-show chillout',
        'An event to celebrate our big show.',
        now() + '9 days'::interval,
        now() + '9 days'::interval + '3 hours'::interval,
        NULL,
        1,
        '{}',
        '1',
        '1',
        -5::NUMERIC(20,17),
        100::NUMERIC(20,17),
        'place'::TEXT);
end;
$d$
;