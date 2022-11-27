DROP TABLE IF EXISTS state;
CREATE TABLE state (
    routine VARCHAR(250),
    instance TIMESTAMP,
    state VARCHAR(250),
    state_time_stamp TIMESTAMP
);