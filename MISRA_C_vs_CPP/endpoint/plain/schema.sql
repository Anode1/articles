CREATE TABLE tokens(token VARCHAR(64) PRIMARY KEY, username VARCHAR(64));
CREATE TABLE items(id IDENTITY PRIMARY KEY, author VARCHAR(64) NOT NULL, name VARCHAR(128) NOT NULL);
INSERT INTO tokens VALUES('t-alice','alice'),('t-bob','bob');
INSERT INTO items(author,name) VALUES('alice','teapot'),('bob','kettle'),('alice','cup'),('carol','saucer'),('alice','spoon');
