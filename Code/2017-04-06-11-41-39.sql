PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE syllabi (
	id INTEGER NOT NULL, 
	basic VARCHAR, 
	description VARCHAR, 
	topics VARCHAR, 
	outcomes VARCHAR, 
	grading VARCHAR, 
	schedule VARCHAR, 
	honesty VARCHAR, 
	deadlines VARCHAR, 
	accessibility VARCHAR, 
	keywords VARCHAR, 
	PRIMARY KEY (id)
);
INSERT INTO "syllabi" VALUES(1,'<ul>
<li>this is section 1 edited again</li>
<li>werk plz</li>
</ul>','Edited by teacher one!</p>
<p>Moar Editing','how did I break this before</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>what if i do this','cool it worky','foo','foo','foo','foo','foo','foo');
INSERT INTO "syllabi" VALUES(2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
INSERT INTO "syllabi" VALUES(3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	name VARCHAR(100), 
	avatar VARCHAR(200), 
	tokens TEXT, 
	created_at DATETIME, 
	admin BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	CHECK (admin IN (0, 1))
);
INSERT INTO "users" VALUES(1,'capstone.teacher.one@gmail.com','Teacher One','https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg','{"access_token": "ya29.GlwjBMQUU9PqgXYwmgV69pTupZkn35dVjaGaPaRWOveelO25xqt-qnLCt2-JbpnXCkh6HUXBzH_lfSqPukwt14ckjWM3kUHR3BZNCKKUBCdU3OXIuNH7OyHAXns8hQ", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjQzN2FhYTAxNGM3YWY3OTI4NjI0YWI1MmZmNjQ0ZDg5ZGVlYjJhYWYifQ.eyJhenAiOiI1NDAzMDI5ODUwNTktNmR2b3J1MXFxcTlhdjl1dDlhOW5yNTA4b2Q0aGlkcTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI1NDAzMDI5ODUwNTktNmR2b3J1MXFxcTlhdjl1dDlhOW5yNTA4b2Q0aGlkcTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDMyOTczMzEyNDgxOTg0MDQzNTgiLCJlbWFpbCI6ImNhcHN0b25lLnRlYWNoZXIub25lQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiLVl3eUhGNFVrS1I4M2E4bUJraWVtQSIsImlzcyI6ImFjY291bnRzLmdvb2dsZS5jb20iLCJpYXQiOjE0OTEzNTAwOTIsImV4cCI6MTQ5MTM1MzY5Mn0.pITDYlskEuSh99ytzzdys10nfs6riJ0J7ia8WfiTOi37NID2mWaWjc0TH4G3gNBFELurXKjVjex3QdMM9vzNQ-OeaL8gHmDk7xDD1U64c6Eo3dF1Int7RpjTtYwtakGqYJ-8C_PVPTeQpLE7Uw3gSK7AWvnaZPIilCIi3d7Y74YnUgXixDYREDTofDHMPgLBXzKOSZUsYu9xlpEkWSz2fUlkfLuOZwcTh1EFuG5mUq3nLyJ3rBorQPFVacWvHY-nFUZHVSAvrNZjLgPuwvKYXYTpp5d6z7_I1bLYQsd7n8Lq0dY4XDI391ioUwwxQ7B1v2FpWo2XKT2BAy6i9vTWYA", "expires_in": 3600, "expires_at": 1491353692.9563086, "token_type": "Bearer"}','2017-03-29 18:46:19.065384',0);
INSERT INTO "users" VALUES(2,'capstone.ad.one@gmail.com','Admin One','https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg','{"expires_in": 3599, "token_type": "Bearer", "access_token": "ya29.GlwlBB9LICXn7kSYG-gD-mRC8mB96MGdW49dAgTQS7z7UJs6jjKwj5Yorc87w2U-vZC2ntTOw_1iN145JRtZGluuvfiHXO32Ytw99wVpY-9zWdJRVn9yWtHr2yovsA", "expires_at": 1491494418.2447624, "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImY3ZjBhMzgxMjUwOTQ0ZWFkMjRlM2EyNDg1MzVlNGE4MDg4OWVhNTIifQ.eyJhenAiOiI1NDAzMDI5ODUwNTktNmR2b3J1MXFxcTlhdjl1dDlhOW5yNTA4b2Q0aGlkcTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI1NDAzMDI5ODUwNTktNmR2b3J1MXFxcTlhdjl1dDlhOW5yNTA4b2Q0aGlkcTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDAyNTk1MTIwMDc2ODg0OTc0MTUiLCJlbWFpbCI6ImNhcHN0b25lLmFkLm9uZUBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6IklfMUNON1NneDNCbHlqazM5bXhXQnciLCJpc3MiOiJhY2NvdW50cy5nb29nbGUuY29tIiwiaWF0IjoxNDkxNDkwODE5LCJleHAiOjE0OTE0OTQ0MTl9.X_7IBWrfiCEKO0JLNvpvF0DvQcSp3cnuafqd_zp1DoqrXqf08FJdW-8p_aHAGPyK8J-mTJLWujaYapKhZvFzNNFiWg7fi3ehw1KAYfQaRKB_t8Rth9RiHIUnSCOa5zSLlR9kRGReVD-wsQhX13gaGzB_0T51ou1_8HXI5AMhRHsUa5IfcHV-s15KLPqc5sH19o1fijbwJ28t1jYRw0xECCHvFvswytjq4f-q5U4Nw0O4nh_Z-MmY0cHSGUnNOPPuV7nE-QPDOVRqfgFGDqqGNFZHeetY8ygIp4OzyN5DAB_TkLB06ou2eUKoWFzjRSGXSLUYNPSMVbp481H3a2A7HA"}','2017-03-29 18:48:40.595907',1);
INSERT INTO "users" VALUES(3,'capstone.teacher.two@gmail.com','Teacher Two','https://lh3.googleusercontent.com/-XdUIqdMkCWA/AAAAAAAAAAI/AAAAAAAAAAA/4252rscbv5M/photo.jpg','{"access_token": "ya29.GlseBOkxy2mJ-QTHQOEyR9QqscRKGXuuPJR5zVkKQr8EU3HTRzPG7p6nGWwTNNjhgk9iUWApB_Mk5uIR6YSvof3uh9jyUpBAn-fUG7QXScu0SnWl_VeqgUdZkap5", "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ2ZWIyMDk0YWMyYjdmNTc2M2RkMzRjYTI3N2EzNDUwZWZiZGI2YTkifQ.eyJhenAiOiI1NDAzMDI5ODUwNTktNmR2b3J1MXFxcTlhdjl1dDlhOW5yNTA4b2Q0aGlkcTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI1NDAzMDI5ODUwNTktNmR2b3J1MXFxcTlhdjl1dDlhOW5yNTA4b2Q0aGlkcTkuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTM5NjQ1Nzc4MDQ3NTI1OTg4MzUiLCJlbWFpbCI6ImNhcHN0b25lLnRlYWNoZXIudHdvQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiaUcyMWlaQmtDRjBmM29vQVIxS2M5dyIsImlzcyI6ImFjY291bnRzLmdvb2dsZS5jb20iLCJpYXQiOjE0OTA4MzY4NTIsImV4cCI6MTQ5MDg0MDQ1Mn0.ECjSklbeqFn0tZIyNw_a-jO2WzYAXuY9NYTqD99_KYyQ6WmuamLKwmLs3iZYOeL2YNoizI28n_kpZcuRtC_Ak11nyn-PlsUQzKXEdTMlu3xJk2Yxjj1Zum0s55AMfQsTG1aQqzLH_N4UQshyzqBNFD-dcddX1geIKfqf1kznjMc5B3jTfaqNw_sNPTg9BaUSP4k79aVWy96pYODMmb6Pnq6_7-rtEjKvKBTcIza22uT9hFXWmU_Z3h1FoV_JT1HoG5vh84NOjQEIuN6wmtKfhCxSjAYTE7_iJstw8ZUWIS__0-OAE_9Azzo5uXrAuxGLk4CXLrB9QWtfrv1MYFpRHw", "token_type": "Bearer", "expires_at": 1490840452.40247, "expires_in": 3600}','2017-03-30 00:51:37.633052',0);
CREATE TABLE courses (
	dept VARCHAR NOT NULL, 
	id INTEGER NOT NULL, 
	section INTEGER NOT NULL, 
	year INTEGER NOT NULL, 
	semester VARCHAR NOT NULL, 
	syllabus INTEGER, 
	user INTEGER, 
	PRIMARY KEY (dept, id, section, year, semester), 
	FOREIGN KEY(syllabus) REFERENCES syllabi (id), 
	FOREIGN KEY(user) REFERENCES users (id)
);
INSERT INTO "courses" VALUES('CS',44101,1,2017,'Spring',1,1);
INSERT INTO "courses" VALUES('CS',10001,1,2017,'spring',2,3);
INSERT INTO "courses" VALUES('CS',10001,2,2017,'spring',3,1);
COMMIT;
