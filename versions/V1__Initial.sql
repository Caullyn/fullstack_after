BEGIN;

    CREATE SCHEMA abuser;
    CREATE SCHEMA geo;
    CREATE SCHEMA band;
    CREATE SCHEMA event;
    CREATE SCHEMA sess;
    CREATE EXTENSION pgcrypto;

    CREATE TABLE abuser.abuser_type (
        ast_id BIGSERIAL PRIMARY KEY,
        ast_type TEXT NOT NULL,
        ast_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        ast_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
    
    INSERT INTO abuser.abuser_type 
    VALUES (DEFAULT, 'One Location', DEFAULT, DEFAULT);
    
    INSERT INTO abuser.abuser_type 
    VALUES (DEFAULT, 'Two Locations', DEFAULT, DEFAULT);
    
    INSERT INTO abuser.abuser_type 
    VALUES (DEFAULT, 'More Locations', DEFAULT, DEFAULT);
    
    CREATE TABLE geo.geo_location (
        geo_id BIGSERIAL PRIMARY KEY,
        geo_description TEXT,
        geo_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        geo_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        
    INSERT INTO geo.geo_location
    VALUES (DEFAULT, 'North America', DEFAULT, DEFAULT);
    
    INSERT INTO geo.geo_location
    VALUES (DEFAULT, 'Europe', DEFAULT, DEFAULT);
    
    CREATE TABLE geo.address (
        add_id BIGSERIAL PRIMARY KEY,
        add_lat NUMERIC(20,17),
        add_lng NUMERIC(20,17),
        add_formatted TEXT
        );
        
    CREATE TABLE abuser.salt (
        sal_id BIGSERIAL PRIMARY KEY,
        sal_salt TEXT NOT NULL,
        sal_geo_id BIGINT REFERENCES geo.geo_location(geo_id) NOT NULL
        );
        
    CREATE TABLE abuser.abuser (
        asr_id BIGSERIAL PRIMARY KEY, 
        asr_user BIGINT UNIQUE NOT NULL,
        asr_email TEXT UNIQUE NOT NULL, 
        asr_password TEXT,
        asr_type_id BIGINT REFERENCES abuser.abuser_type(ast_id) NOT NULL DEFAULT 1,
        asr_geo_id BIGINT REFERENCES geo.geo_location(geo_id) NOT NULL,
        asr_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        asr_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
    
    CREATE TABLE sess.session (
        ses_id BIGSERIAL PRIMARY KEY,
        ses_user BIGINT REFERENCES abuser.abuser(asr_user) NOT NULL,
        ses_session TEXT NOT NULL,
        ses_expired BOOLEAN NOT NULL DEFAULT FALSE,
        ses_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        ses_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        
    CREATE TABLE band.band (
        ban_id BIGSERIAL PRIMARY KEY,
        ban_user BIGINT REFERENCES abuser.abuser(asr_user) NOT NULL,
        ban_geo_id BIGINT REFERENCES geo.geo_location(geo_id) NOT NULL,
        ban_name TEXT NOT NULL,
        ban_email TEXT,
        ban_description TEXT,
        ban_detail JSON,
        ban_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        ban_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        
    CREATE TABLE band.image (
        big_id BIGSERIAL PRIMARY KEY,
        big_ban_id BIGINT REFERENCES band.band(ban_id) NOT NULL,
        big_name TEXT NOT NULL,
        big_description TEXT NOT NULL,
        big_image BYTEA
        );
         
    CREATE TABLE event.event (
        evt_id BIGSERIAL PRIMARY KEY,
        evt_asr_user BIGINT REFERENCES abuser.abuser(asr_user) NOT NULL,
        evt_name TEXT NOT NULL,
        evt_description TEXT,
        evt_start TIMESTAMP WITH TIME ZONE NOT NULL,
        evt_end TIMESTAMP WITH TIME ZONE,
        evt_geo_id BIGINT REFERENCES geo.geo_location (geo_id) NOT NULL,
        evt_add_id BIGINT REFERENCES geo.address(add_id) NOT NULL,
        evt_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        evt_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        
    CREATE TABLE event.event_image (
        evi_id BIGSERIAL PRIMARY KEY,
        evi_evt_id BIGINT REFERENCES event.event(evt_id),
        evi_img TEXT NOT NULL,
        evi_type TEXT NOT NULL,
        evi_default BOOLEAN DEFAULT FALSE,
        evi_created TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
        evi_modified TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        
    CREATE TABLE event.event_band(
        evb_id BIGSERIAL PRIMARY KEY,
        evb_ban_id BIGINT,
        evb_evt_id BIGINT
        );
    
    CREATE UNIQUE INDEX uqc_event_band ON event.event_band(evb_ban_id, evb_evt_id);
    
    INSERT INTO abuser.salt values (DEFAULT, 'gfruc5', 1);
    INSERT INTO abuser.salt values (DEFAULT, 'gfcur5', 2);
COMMIT;