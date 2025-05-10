/*
   drop all tables
*/
drop table if exists questions cascade;
drop table if exists answers;


/*
   questions
*/

create table questions (
   id         serial primary key,
   title      varchar(300),
   body_md    varchar(500),
   tsv        tsvector,
   created_at timestamp
);

create index questions_tsv_gin on questions using gin(tsv);

create trigger tsvectorupdate 
   before insert or update 
      on questions
for each row execute procedure
   tsvector_update_trigger(tsv, 'pg_catalog.russian', title)
;

/*
   answers
*/
create table answers (
   id          serial primary key,
   question_id integer not null,
   body_md     varchar(3000),
   ldm         date not null default current_date,
   constraint fk_question foreign key ( question_id )
      references questions ( id )
         on delete cascade
);