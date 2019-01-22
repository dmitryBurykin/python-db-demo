CREATE TABLE IF NOT EXISTS Speciality(
  id integer PRIMARY KEY AUTOINCREMENT,
  name text NOT NULL,
  description text,
  code text
);

CREATE TABLE IF NOT EXISTS Student(
  id integer PRIMARY KEY AUTOINCREMENT,
  name text NOT NULL,
  age integer NOT NULL,
  sex text NOT NULL,
  speciality_id integer NOT NULL
);