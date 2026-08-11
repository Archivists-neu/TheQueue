-- Database creation
DROP DATABASE IF EXISTS `the-queue-db`;
CREATE DATABASE `the-queue-db`;
USE `the-queue-db`;


-- Tables creation
DROP TABLE IF EXISTS location;
CREATE TABLE location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(75),
    state VARCHAR(75),
    country VARCHAR(75)
);

DROP TABLE IF EXISTS user;
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_uuid CHAR(36) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    dob DATE,
    gender VARCHAR(30),
    account_status ENUM('online', 'busy', 'offline', 'custom') DEFAULT 'offline' NOT NULL,
    custom_status_message VARCHAR(150),
    date_account_creation DATETIME NOT NULL,
    date_account_deletion DATETIME,
    location_id INT NOT NULL,
    CONSTRAINT fk_user_location
        FOREIGN KEY (location_id) REFERENCES location(location_id)
);

DROP TABLE IF EXISTS genre;
CREATE TABLE genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(75) NOT NULL,
    description TEXT
);

DROP TABLE IF EXISTS media;
CREATE TABLE media (
    media_id INT AUTO_INCREMENT PRIMARY KEY,
    media_type ENUM('book', 'tvshow', 'game', 'movie') NOT NULL,
    title VARCHAR(150) NOT NULL,
    summary TEXT,
    release_date DATE
);

DROP TABLE IF EXISTS media_genre;
CREATE TABLE media_genre (
    media_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (media_id, genre_id),
    CONSTRAINT fk_media_genre_media
        FOREIGN KEY (media_id) REFERENCES media(media_id),
    CONSTRAINT fk_media_genre_genre
        FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

DROP TABLE IF EXISTS review;
CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    review_comment TEXT,
    likes INT DEFAULT 0,
    review_date DATETIME NOT NULL,
    user_id INT NOT NULL,
    media_id INT NOT NULL,
    location_id INT,
    CONSTRAINT fk_review_user
        FOREIGN KEY (user_id) REFERENCES user(user_id),
    CONSTRAINT fk_review_media
        FOREIGN KEY (media_id) REFERENCES media(media_id),
    CONSTRAINT fk_review_location
        FOREIGN KEY (location_id) REFERENCES location(location_id)
);

DROP TABLE IF EXISTS comment;
CREATE TABLE comment (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    comment_message TEXT NOT NULL,
    likes INT DEFAULT 0,
    comment_date DATETIME NOT NULL,
    user_id INT NOT NULL,
    review_id INT NOT NULL,
    CONSTRAINT fk_comment_user
        FOREIGN KEY (user_id) REFERENCES user(user_id),
    CONSTRAINT fk_comment_review
        FOREIGN KEY (review_id) REFERENCES review(review_id)
);

DROP TABLE IF EXISTS friendship;
CREATE TABLE friendship (
    friendship_id INT AUTO_INCREMENT PRIMARY KEY,
    requester_id INT NOT NULL,
    addressee_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'declined', 'blocked') DEFAULT 'pending' NOT NULL,
    date_requested DATETIME NOT NULL,
    date_accepted DATETIME,
    CONSTRAINT fk_friendship_requester
        FOREIGN KEY (requester_id) REFERENCES user(user_id),
    CONSTRAINT fk_friendship_addressee
        FOREIGN KEY (addressee_id) REFERENCES user(user_id),
    UNIQUE INDEX idx_friendship (requester_id, addressee_id)
);

DROP TABLE IF EXISTS friendship_common_interest;
CREATE TABLE friendship_common_interest (
    friendship_id INT NOT NULL,
    media_id INT NOT NULL,
    PRIMARY KEY (friendship_id, media_id),
    CONSTRAINT fk_common_interest_friendship
        FOREIGN KEY (friendship_id) REFERENCES friendship(friendship_id),
    CONSTRAINT fk_common_interest_media
        FOREIGN KEY (media_id) REFERENCES media(media_id)
);

DROP TABLE IF EXISTS recommendation;
CREATE TABLE recommendation (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    recommendation_date DATETIME NOT NULL,
    attached_message TEXT,
    friendship_id INT NOT NULL,
    media_id INT NOT NULL,
    CONSTRAINT fk_recommendation_friendship
        FOREIGN KEY (friendship_id) REFERENCES friendship(friendship_id),
    CONSTRAINT fk_recommendation_media
        FOREIGN KEY (media_id) REFERENCES media(media_id)
);


-- Sample data creation
INSERT INTO location (city,state,country)
    VALUES ('Boston','Massachusetts','United States'),
           ('Miami','Florida','United States'),
           ('New York City','New York','United States');

INSERT INTO user (user_uuid,first_name,last_name,email,phone,dob,gender,
    Account_status,custom_status_message,date_account_creation,location_id)
    VALUES (UUID(),'Maya','Lopez','maya.lopez@gmail.com',
            '6175551234','2002-04-15','Female','online',
            NULL,'2026-01-10 14:30:00',1),
           (UUID(),'Daniel','Kim','daniel.kim@gmail.com',
            '3055555678','2001-09-22','Male','busy',
            NULL,'2026-02-05 10:15:00',2),
           (UUID(),'Alex','Rivera','alex.rivera@gmail.com',
            NULL,'2003-06-11','Nonbinary','custom',
            'Currently reading','2026-03-12 18:45:00',3);

INSERT INTO genre (name, description)
    VALUES ('Fantasy', 'Stories containing magical or supernatural elements.'),
           ('Science Fiction', 'Stories involving futuristic science and 
 technology.'),
           ('Mystery', 'Stories centered around solving mysteries or crimes.');

INSERT INTO media (media_type,title,summary,release_date)
    VALUES ('book','The Hobbit','A hobbit embarks on an unexpected adventure.',
            '1937-09-21'),
           ('movie','Interstellar','Explorers travel through space in search of
            a new home for humanity.','2014-11-07'),
           ('game','The Legend of Zelda: Breath of the Wild','An open-world
            adventure through the kingdom of Hyrule.','2017-03-03');

INSERT INTO media_genre
    VALUES (1, 1),
           (2, 2),
           (3, 1);

INSERT INTO review (review_comment,likes,review_date,user_id,media_id,location_id)
    VALUES ('A classic adventure that still holds up.',12,
            '2026-05-02 19:30:00',1,1,1),
           ('The visuals and soundtrack were incredible.',25,
            '2026-05-04 21:15:00',2,2,2),
           ('One of my favorite open-world games.',18,
            '2026-05-07 16:45:00',3,3,3);

INSERT INTO comment (comment_message,likes,comment_date,user_id,review_id)
    VALUES ('I loved this book too!',4,'2026-05-02 20:00:00',2,1),
           ('The soundtrack is definitely my favorite part.',7,
 '2026-05-04 22:10:00',1,2),
           ('I spent way too many hours exploring Hyrule.',5,
 '2026-05-07 18:00:00',1,3);

INSERT INTO friendship (requester_id,addressee_id,status,date_requested,date_accepted)
    VALUES (1,2,'accepted','2026-03-01 12:00:00','2026-03-01 15:30:00'),
           (1,3,'accepted','2026-03-05 09:30:00','2026-03-06 11:00:00'),
           (2,3,'pending','2026-05-10 14:00:00',NULL);

INSERT INTO friendship_common_interest
    VALUES (1, 1),
           (1, 2),
           (2, 3);

INSERT INTO recommendation (recommendation_date,attached_message,friendship_id,media_id)
    VALUES ('2026-05-12 18:30:00','I think you would really like this!',1,1),
           ('2026-05-14 20:00:00','You have to watch this one.',1,2),
           ('2026-05-16 13:15:00','This game seems right up your alley.',2,3);
