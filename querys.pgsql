CREATE TABLE users(
    id_user serial PRIMARY KEY,
    username varchar not null,
    password varchar not null    
);


CREATE TABLE todo(
    id_todo serial PRIMARY KEY,
    user_id INTEGER null,
    text varchar not null,
    complete boolean null
);

select * from users