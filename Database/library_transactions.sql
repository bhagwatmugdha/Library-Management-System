-- MySQL dump 10.13  Distrib 5.7.23, for Linux (x86_64)
--
-- Host: localhost    Database: library
-- ------------------------------------------------------
-- Server version	5.7.23-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transactions` (
  `transaction_id` int(11) NOT NULL AUTO_INCREMENT,
  `studentUsername` varchar(100) DEFAULT NULL,
  `staffUsername` varchar(100) DEFAULT NULL,
  `book_id` int(11) DEFAULT NULL,
  `issueDate` datetime DEFAULT NULL,
  `returnDate` datetime DEFAULT NULL,
  `fine` int(11) DEFAULT '0',
  `Done` int(11) DEFAULT '0',
  `bookName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `book_id` (`book_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` (`transaction_id`, `studentUsername`, `staffUsername`, `book_id`, `issueDate`, `returnDate`, `fine`, `Done`, `bookName`) VALUES (12,'161070000','171070050',7,'2018-10-18 22:21:03','2018-10-25 22:21:03',0,1,'newTest'),(16,'161070000','171070050',7,'2018-10-18 22:31:39','2018-10-25 22:31:39',0,1,'newTest'),(17,'161070000','171070050',2,'2018-10-18 22:31:48','2018-10-25 22:31:48',90,0,'Networking Systems by Tannenbaum'),(18,'161070000','shubhada',4,'2018-10-18 22:31:56','2018-10-25 22:31:56',90,0,'AI by Deepak Khimani'),(19,'161070000','shubhada',3,'2018-10-18 22:32:05','2018-10-25 22:32:05',90,0,'Software Engineering by Pressman'),(20,'161070000','171071050',7,'2018-10-18 22:35:11','2018-10-25 22:35:11',0,1,'newTest');
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER set_date BEFORE INSERT ON `transactions` 
FOR EACH ROW SET
    NEW.issueDate = IFNULL(NEW.issueDate, NOW()),
    NEW.returnDate = TIMESTAMPADD(DAY, 7, NEW.issueDate) */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-10-18 22:54:04
