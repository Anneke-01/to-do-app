CREATE TABLE users(
    id_user serial PRIMARY KEY,
    username varchar not null,
    password varchar not null
);

CREATE TABLE todo(
    id_todo serial PRIMARY KEY,
    user_id INTEGER REFERENCES users(id_user) null,
    text varchar not null,
    complete boolean null
);

select * from users
select * from todo

SELECT id_user FROM users WHERE username='Anneke'
SELECT * FROM todo WHERE user_id=2 and complete=false
UPDATE todo SET complete=true WHERE id_todo=2
UPDATE todo SET complete=true WHERE id_todo=4 and user_id=2
DELETE FROM todo  WHERE complete=true and user_id=2