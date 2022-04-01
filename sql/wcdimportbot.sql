CREATE TABLE `hash` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `hash` varchar(32) unique
);
CREATE INDEX hash_index ON hash(hash);