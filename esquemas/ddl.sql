CREATE MATERIALIZED VIEW scrobbles_mb AS (
    SELECT following_username
    FROM follows
    WHERE follower_username = "mbarretov2"
);

CREATE MATERIALIZED VIEW scrobbles_vic AS (
    SELECT following_username
    FROM follows
    WHERE follower_username = "vicisnotonfire"
);

CREATE MATERIALIZED VIEW scrobbles24 AS (
    SELECT *
    FROM scrobbles
    WHERE extract(year FROM scrobble_date) = 2024
);

CREATE TABLE control_panel (
	id bigserial PRIMARY KEY,
	chave TEXT,
	description TEXT,
	status integer,
	start_date timestamp,
	end_date timestamp,
	insertion_date timestamp DEFAULT now()
);


-- Remoção de duplicatas
DELETE FROM scrobbles WHERE (username, artist, scrobble_date, track, insertion_date) IN
(SELECT s1.username, s1.artist, s1.scrobble_date, s1.track, s1.insertion_date FROM scrobbles s1, scrobbles s2
WHERE s1.artist = s2.artist AND s1.username = s2.username AND s1.scrobble_date = s2.scrobble_date AND s1.track = s2.track
AND s1.insertion_date > s2.insertion_date);