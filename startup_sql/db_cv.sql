create table if not exists user
(
    id         int auto_increment primary key,
    last_name  varchar(100) not null,
    first_name varchar(100) not null,
    cv_url     varchar(255) null
);

create table if not exists skill
(
    id   int auto_increment primary key,
    name varchar(100) not null,
    constraint skill_name_uindex unique (name)
);

create table if not exists user_skill_association
(
    user_id  int not null,
    skill_id int not null,
    level    int not null,
    primary key (user_id, skill_id)
);