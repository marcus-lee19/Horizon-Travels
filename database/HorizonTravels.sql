CREATE DATABASE  IF NOT EXISTS `horizon_travels` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `horizon_travels`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: horizon_travels
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `booking_status`
--

DROP TABLE IF EXISTS `booking_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking_status` (
  `status_id` int NOT NULL AUTO_INCREMENT,
  `status_name` varchar(30) NOT NULL,
  `refund_percent` int DEFAULT NULL,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_name` (`status_name`),
  CONSTRAINT `booking_status_chk_1` CHECK ((`refund_percent` between 0 and 100))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking_status`
--

LOCK TABLES `booking_status` WRITE;
/*!40000 ALTER TABLE `booking_status` DISABLE KEYS */;
INSERT INTO `booking_status` VALUES (1,'Not Used',0),(2,'Used',0),(3,'Cancelled',0),(4,'Partially Refunded',60),(5,'Fully Refunded',100);
/*!40000 ALTER TABLE `booking_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `flight_times`
--

DROP TABLE IF EXISTS `flight_times`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `flight_times` (
  `flight_id` int NOT NULL AUTO_INCREMENT,
  `depart` varchar(50) DEFAULT NULL,
  `dep_time` time DEFAULT NULL,
  `arrive` varchar(50) DEFAULT NULL,
  `arr_time` time DEFAULT NULL,
  `original_price` float DEFAULT NULL,
  PRIMARY KEY (`flight_id`)
) ENGINE=InnoDB AUTO_INCREMENT=76 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `flight_times`
--

LOCK TABLES `flight_times` WRITE;
/*!40000 ALTER TABLE `flight_times` DISABLE KEYS */;
INSERT INTO `flight_times` VALUES (1,'Newcastle','17:45:00','Bristol','19:30:00',90),(2,'Bristol','09:00:00','Newcastle','10:15:00',90),(3,'Cardiff','07:00:00','Edinburgh','08:30:00',80),(4,'Bristol','12:30:00','Manchester','13:30:00',80),(5,'Manchester','13:20:00','Bristol','14:20:00',80),(6,'Bristol','07:40:00','London','08:20:00',100),(7,'London','13:00:00','Manchester','14:00:00',100),(8,'Manchester','12:20:00','Glasgow','13:30:00',80),(9,'Bristol','08:40:00','Glasgow','09:45:00',100),(10,'Glasgow','14:30:00','Newcastle','15:45:00',100),(11,'Newcastle','16:15:00','Manchester','17:05:00',80),(12,'Manchester','18:25:00','Bristol','19:30:00',80),(13,'Bristol','06:20:00','Manchester','07:20:00',80),(14,'Portsmouth','12:00:00','Dundee','14:00:00',120),(15,'Dundee','10:00:00','Portsmouth','12:00:00',100),(16,'Edinburgh','18:30:00','Cardiff','20:00:00',90),(17,'Southampton','12:00:00','Manchester','13:30:00',90),(18,'Manchester','19:00:00','Southampton','20:30:00',90),(19,'Birmingham','17:00:00','Newcastle','17:45:00',100),(20,'Newcastle','07:00:00','Birmingham','07:45:00',100),(22,'Aberdeen','08:00:00','Portsmouth','09:30:00',100);
/*!40000 ALTER TABLE `flight_times` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `reference` int NOT NULL,
  `class` varchar(45) NOT NULL,
  `seat_count` int NOT NULL,
  `price` float NOT NULL,
  `flight_id` int NOT NULL,
  `user_id` int NOT NULL,
  `flight_date` date NOT NULL,
  `booking_date` date DEFAULT NULL,
  `status_id` int DEFAULT '1',
  PRIMARY KEY (`reference`),
  KEY `fk_tickets_flight` (`flight_id`),
  KEY `fk_tickets_user` (`user_id`),
  KEY `fk_ticket_status` (`status_id`),
  CONSTRAINT `fk_ticket_status` FOREIGN KEY (`status_id`) REFERENCES `booking_status` (`status_id`),
  CONSTRAINT `fk_tickets_flight` FOREIGN KEY (`flight_id`) REFERENCES `flight_times` (`flight_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_tickets_user` FOREIGN KEY (`user_id`) REFERENCES `user_accounts` (`userID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tickets`
--

LOCK TABLES `tickets` WRITE;
/*!40000 ALTER TABLE `tickets` DISABLE KEYS */;
INSERT INTO `tickets` VALUES (2244030,'Business',26,4680,1,4,'2025-05-01','2025-04-30',1),(5549991,'Economy',3,202.5,18,7,'2025-07-17','2025-04-27',5),(6891479,'Business',1,180,6,28,'2025-06-17','2025-05-01',4),(8742458,'Business',1,180,1,4,'2025-05-02','2025-04-30',1),(12472946,'Economy',3,300,19,4,'2025-04-25','2025-04-24',3),(16172950,'Business',3,540,19,3,'2025-06-12','2025-04-24',1),(17601788,'Economy',2,180,2,4,'2025-05-02','2025-04-27',3),(23285870,'Economy',1,75,15,7,'2025-07-18','2025-04-27',1),(24140058,'Economy',3,225,15,3,'2025-07-18','2025-04-24',5),(25374445,'Business',2,324,17,4,'2025-06-19','2025-04-27',1),(40342459,'Economy',3,216,11,8,'2025-06-19','2025-04-21',1),(42709011,'Business',5,850,7,3,'2025-07-03','2025-04-24',5),(42815015,'Economy',3,300,20,3,'2025-04-24','2025-04-24',2),(47188944,'Business',1,200,6,4,'2025-05-01','2025-05-01',1),(55511891,'Economy',2,160,5,7,'2025-04-30','2025-04-28',1),(57519630,'Business',1,180,2,28,'2025-05-07','2025-05-01',1),(57539881,'Economy',3,216,13,4,'2025-06-26','2025-04-23',1),(60469383,'Economy',1,100,6,3,'2025-04-28','2025-04-27',2),(61600654,'Economy',3,240,3,4,'2025-04-25','2025-04-24',2),(70745870,'Business',5,850,7,18,'2025-07-09','2025-04-22',1),(71185125,'Business',1,136,13,4,'2025-06-30','2025-04-24',1),(71343869,'Economy',2,200,15,4,'2025-04-28','2025-04-27',2),(71382358,'Business',3,408,13,4,'2025-07-01','2025-04-21',5),(72182588,'Business',3,432,13,18,'2025-06-19','2025-04-23',1),(76147250,'Business',1,136,5,7,'2025-07-16','2025-04-28',1),(84073097,'Economy',16,1280,11,7,'2025-04-23','2025-04-21',2),(84923086,'Economy',88,7040,11,8,'2025-04-23','2025-04-21',2),(85554727,'Business',21,3024,13,4,'2025-06-20','2025-04-23',4),(86139217,'Economy',3,300,6,4,'2025-04-23','2025-04-23',2),(86523748,'Economy',2,180,17,18,'2025-04-28','2025-04-25',2),(91619679,'Business',3,510,7,19,'2025-06-30','2025-04-26',1),(93305760,'Economy',3,240,3,4,'2025-04-25','2025-04-24',2),(96803586,'Business',5,800,13,4,'2025-06-20','2025-04-21',4),(97092019,'Business',12,1920,4,14,'2025-04-28','2025-04-26',2),(97211617,'Economy',2,150,6,19,'2025-07-21','2025-04-26',1);
/*!40000 ALTER TABLE `tickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_accounts`
--

DROP TABLE IF EXISTS `user_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_accounts` (
  `userID` int NOT NULL AUTO_INCREMENT,
  `fname` varchar(45) NOT NULL,
  `lname` varchar(45) NOT NULL,
  `email` varchar(45) NOT NULL,
  `phnum` varchar(15) NOT NULL,
  `passwd` varchar(128) NOT NULL,
  `user_type` varchar(8) DEFAULT 'standard',
  PRIMARY KEY (`userID`),
  UNIQUE KEY `userID_UNIQUE` (`userID`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `passwd_UNIQUE` (`passwd`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_accounts`
--

LOCK TABLES `user_accounts` WRITE;
/*!40000 ALTER TABLE `user_accounts` DISABLE KEYS */;
INSERT INTO `user_accounts` VALUES (3,'Sadie','Enward','sadieenward@gmail.com','12345','$5$rounds=535000$dmEOcffkr6mhUi/B$FqUB34cPAvIi65BYLFgRmUAgTOUPf0Vv4ruPnvMNiX9','standard'),(4,'Marcus','Lee','marcuslee@gmail.com','07777936807','$5$rounds=535000$viCHEQ5x1f96Wtb1$LJ426ygpL4gVdoWaRilbX5SWXfIMOczIquXeBB3XAW7','standard'),(7,'Ray','Cist','raycist@gmail.com','6699','$5$rounds=535000$9RxeV2uOBAB/4Qbu$w0VRmQ2ESgXGbbJV2dy1CURLEuAF8tTUMXXuDoYrix0','standard'),(8,'Benjamin','Dover','bendover@gmail.com','69696969','$5$rounds=535000$Va8ehjF2moAdGpNb$NhfqGyGPMSXRYXlGKfLHIbo80fZionmdu9jbi9DaM4.','standard'),(11,'Fernando','Alonso','fernandoalonso@gmail.com','090000014','$5$rounds=535000$pTiy3046WaNgYHyW$Bec88fnk2Kr2GsVbsmpt.YpPk.BbI7JwBxoCf46h2P2','standard'),(13,'Marcus','Lee','marcuslee@admin.com','0999999999','$5$rounds=535000$0GbDHUlnQ57wzfg5$ngJEhm4/7miR85Ez9q0L7xaydq3EzQXjGOSIP4Rt26A','admin'),(14,'Moe','Lester','moelester@gmail.com','99999','$5$rounds=535000$Q2JjTFOmO9smd1dz$thQbzNAYY9wgvWbw1AYrZCXZDxE/hBZyoC8vrpbMOYD','standard'),(17,'Bruh','Brother','bruh@gmail.com','999','$5$rounds=535000$eYafv./y2UOf1FgN$1iZjTkruqSBU1gUeGILZPIdXipvUvgnOoiKbnteQ0zC','standard'),(18,'Mike','Hunt','mikehunt@gmail.com','099999','$5$rounds=535000$31Wa3wDZCzkUJ/W7$kBxFoLZvLGIc/dipIe6WcIq8W.Id/cIzxR0DqTmdr0C','standard'),(19,'Arthur','Morgan','arthurmorgan@gmail.com','07123456789','$5$rounds=535000$DG/w2dbvkng/NIZL$NpfKo75/QMjsoISdeLCU3/i7qQZq5x5fcO0/4W54RF5','standard'),(28,'Marcus','Lee','mlee@user.com','0912345','$5$rounds=535000$odOMPqS7BC50Bsa/$d..KblsmNiooSe.AuOywnbLl3kmCtBKlIL729otmvm5','standard');
/*!40000 ALTER TABLE `user_accounts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-01  7:17:22
