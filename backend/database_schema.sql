/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.6.23-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: clubinfo_afc
-- ------------------------------------------------------
-- Server version	12.3.2-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `RECOVER_YOUR_DATA`
--

DROP TABLE IF EXISTS `RECOVER_YOUR_DATA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `RECOVER_YOUR_DATA` (
  `text` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article` (
  `ArticleId` int(11) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) DEFAULT NULL,
  `Heading` varchar(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Writer` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `Dated` datetime DEFAULT NULL,
  `Content` text DEFAULT NULL,
  `Image` varchar(80) DEFAULT NULL,
  `Caption` mediumtext DEFAULT NULL,
  `Status` tinyint(1) DEFAULT 1,
  `OrderNo` int(11) NOT NULL,
  `Urdu` tinyint(1) NOT NULL DEFAULT 0,
  `CreatedBy` int(11) DEFAULT NULL,
  `UpdatedBy` int(11) DEFAULT NULL,
  `CreatedAt` datetime DEFAULT NULL,
  `UpdatedAt` datetime DEFAULT NULL,
  `Category` int(11) DEFAULT NULL,
  PRIMARY KEY (`ArticleId`)
) ENGINE=InnoDB AUTO_INCREMENT=3116 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article_group`
--

DROP TABLE IF EXISTS `article_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_group` (
  `GroupId` int(11) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `Heading` varchar(100) DEFAULT NULL,
  `HeadArticle` int(11) DEFAULT NULL,
  `Image` varchar(80) DEFAULT NULL,
  `Caption` varchar(200) DEFAULT NULL,
  `Status` tinyint(1) DEFAULT 1,
  `DispOrder` int(11) DEFAULT NULL,
  PRIMARY KEY (`GroupId`)
) ENGINE=InnoDB AUTO_INCREMENT=459 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article_tags`
--

DROP TABLE IF EXISTS `article_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `article_tags` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ArticleId` int(11) NOT NULL,
  `ObjectType` varchar(20) NOT NULL,
  `ObjectId` int(11) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `ArticleId` (`ArticleId`,`ObjectType`,`ObjectId`)
) ENGINE=MyISAM AUTO_INCREMENT=1341 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `association`
--

DROP TABLE IF EXISTS `association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `association` (
  `AssociationId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `AssociationName` varchar(45) NOT NULL DEFAULT ' ',
  `President` varchar(45) DEFAULT ' ',
  `Secretary` varchar(45) DEFAULT ' ',
  `Valid` tinyint(1) NOT NULL DEFAULT 1,
  `City` varchar(45) DEFAULT ' ',
  `Treasurer` varchar(45) DEFAULT ' ',
  `RegionId` int(11) NOT NULL,
  `PresidentContact` varchar(100) DEFAULT NULL,
  `SecretaryContact` varchar(100) DEFAULT NULL,
  `TreasurerContact` varchar(100) DEFAULT NULL,
  `PresidentPic` int(1) DEFAULT 0,
  `SecretaryPic` int(1) DEFAULT 0,
  `TreasurerPic` int(1) DEFAULT 0,
  `ShortName` varchar(10) NOT NULL,
  PRIMARY KEY (`AssociationId`)
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ball_by_ball`
--

DROP TABLE IF EXISTS `ball_by_ball`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ball_by_ball` (
  `BallId` int(11) NOT NULL AUTO_INCREMENT,
  `MatchNo` int(11) DEFAULT NULL,
  `Innings` int(11) DEFAULT NULL,
  `Over` int(11) DEFAULT NULL,
  `Ball` int(11) DEFAULT NULL,
  `BatsmanId` int(11) DEFAULT NULL,
  `BowlerId` int(11) DEFAULT NULL,
  `Runs` int(11) DEFAULT 0,
  `Strike` int(1) DEFAULT 1,
  `Wide` int(1) DEFAULT 0,
  `NoBall` int(1) DEFAULT 0,
  `LegByes` int(1) DEFAULT 0,
  `Byes` int(1) DEFAULT 0,
  `Wicket` int(1) DEFAULT 0,
  `Comment` varchar(100) DEFAULT NULL,
  `BallPitch` varchar(40) DEFAULT NULL,
  `ShotPosition` varchar(10) DEFAULT NULL,
  `ShotArea` varchar(50) DEFAULT NULL,
  `Inverse` int(1) DEFAULT 0,
  `FreeHit` int(11) DEFAULT NULL,
  `Penalty` int(11) DEFAULT NULL,
  `ShotType` int(11) NOT NULL DEFAULT 0,
  `BatsmanName` varchar(100) DEFAULT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`BallId`)
) ENGINE=InnoDB AUTO_INCREMENT=37873 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `batting_detail`
--

DROP TABLE IF EXISTS `batting_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `batting_detail` (
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `PlayerId` int(11) NOT NULL,
  `Runs` int(11) DEFAULT 0,
  `BallsFaced` int(11) DEFAULT 0,
  `Fours` int(11) DEFAULT 0,
  `Sixes` int(11) DEFAULT 0,
  `Singles` int(11) DEFAULT 0,
  `Doubles` int(11) DEFAULT 0,
  `Threes` int(11) DEFAULT 0,
  `Dots` int(11) DEFAULT 0,
  `NotOut` tinyint(1) DEFAULT NULL,
  `HowOut` varchar(20) DEFAULT NULL,
  `OutDetail` varchar(50) DEFAULT NULL,
  `Bowler` int(11) DEFAULT NULL,
  `Fielder` int(11) DEFAULT NULL,
  `Position` int(11) DEFAULT 0,
  `UpdateBy` int(11) NOT NULL,
  `LastUpdated` datetime NOT NULL,
  `BatsmanName` varchar(100) DEFAULT NULL,
  `FielderName` varchar(100) DEFAULT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `TeamId` int(11) DEFAULT NULL,
  `TeamName` varchar(100) DEFAULT NULL,
  `MatchType` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`,`PlayerId`),
  KEY `batting_player_fkey` (`PlayerId`) USING BTREE,
  CONSTRAINT `FK_batting_detail_innings` FOREIGN KEY (`MatchNo`, `Innings`) REFERENCES `innings` (`MatchNo`, `Innings`),
  CONSTRAINT `FK_batting_detail_player` FOREIGN KEY (`PlayerId`) REFERENCES `player` (`PlayerId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `batting_stats`
--

DROP TABLE IF EXISTS `batting_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `batting_stats` (
  `PlayerId` int(11) NOT NULL,
  `Season` varchar(10) NOT NULL,
  `Stage` varchar(20) NOT NULL,
  `Format` varchar(10) NOT NULL,
  `ICC` varchar(20) DEFAULT NULL,
  `Matches` int(10) unsigned DEFAULT 0,
  `Inn` int(10) unsigned DEFAULT 0,
  `NotOut` int(10) unsigned DEFAULT 0,
  `Runs` int(10) unsigned DEFAULT 0,
  `HS` int(10) unsigned DEFAULT 0,
  `Average` decimal(6,2) DEFAULT NULL,
  `BF` int(10) unsigned DEFAULT 0,
  `SR` decimal(6,2) DEFAULT NULL,
  `Hundreds` int(10) unsigned DEFAULT 0,
  `Fifties` int(10) unsigned DEFAULT 0,
  `Zeros` int(10) unsigned DEFAULT 0,
  `Fours` int(10) unsigned DEFAULT 0,
  `Sixes` int(10) unsigned DEFAULT 0,
  `Catches` int(11) DEFAULT NULL,
  `Stumps` int(11) DEFAULT NULL,
  `PlayerName` varchar(50) NOT NULL,
  `LastMatch` int(11) DEFAULT 0,
  PRIMARY KEY (`PlayerId`,`Season`,`Stage`,`Format`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bowling_detail`
--

DROP TABLE IF EXISTS `bowling_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bowling_detail` (
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `PlayerId` int(11) NOT NULL,
  `Overs` double DEFAULT 0,
  `Maiden` int(11) DEFAULT 0,
  `Runs` int(11) DEFAULT 0,
  `Wickets` int(11) DEFAULT 0,
  `Wides` int(11) DEFAULT 0,
  `NoBalls` int(11) DEFAULT 0,
  `TeamId` int(11) DEFAULT NULL,
  `TeamName` varchar(45) NOT NULL,
  `Position` int(11) DEFAULT 0,
  `Current` int(11) NOT NULL,
  `UpdateBy` int(11) NOT NULL,
  `LastUpdate` datetime NOT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `MatchType` varchar(1) DEFAULT NULL,
  `Balls` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`,`PlayerId`),
  KEY `bowling_player_fkey` (`PlayerId`) USING BTREE,
  CONSTRAINT `FK_bowling_detail_innings` FOREIGN KEY (`MatchNo`, `Innings`) REFERENCES `innings` (`MatchNo`, `Innings`),
  CONSTRAINT `FK_bowling_detail_player` FOREIGN KEY (`PlayerId`) REFERENCES `player` (`PlayerId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bowling_stats`
--

DROP TABLE IF EXISTS `bowling_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `bowling_stats` (
  `PlayerId` int(11) NOT NULL,
  `Season` varchar(10) NOT NULL,
  `Stage` varchar(20) NOT NULL,
  `Format` varchar(10) NOT NULL,
  `ICC` varchar(20) DEFAULT NULL,
  `Matches` int(10) unsigned DEFAULT 0,
  `Inn` int(10) unsigned DEFAULT 0,
  `Balls` int(10) unsigned DEFAULT 0,
  `Runs` int(10) unsigned DEFAULT 0,
  `Wickets` int(10) unsigned DEFAULT 0,
  `BBI` varchar(8) DEFAULT NULL,
  `BBM` varchar(8) DEFAULT '0',
  `Average` decimal(6,2) DEFAULT NULL,
  `Economy` decimal(6,2) DEFAULT NULL,
  `StrikeRate` decimal(6,2) DEFAULT NULL,
  `Fourfor` int(10) unsigned DEFAULT 0,
  `Fivefor` int(10) unsigned DEFAULT 0,
  `Tenfor` int(10) unsigned DEFAULT 0,
  `PlayerName` varchar(50) NOT NULL,
  `LastMatch` int(11) DEFAULT 0,
  PRIMARY KEY (`PlayerId`,`Season`,`Stage`,`Format`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `budget`
--

DROP TABLE IF EXISTS `budget`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `budget` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `BudgetMonth` date DEFAULT NULL,
  `HeadId` int(11) DEFAULT NULL,
  `Amount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `fk_budget_sectionhead` (`HeadId`),
  CONSTRAINT `fk_budget_sectionhead` FOREIGN KEY (`HeadId`) REFERENCES `section_head` (`HeadId`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `category` (
  `CatId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `CatName` varchar(50) NOT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`CatId`),
  UNIQUE KEY `CatName` (`CatName`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `city`
--

DROP TABLE IF EXISTS `city`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `city` (
  `CityId` int(11) NOT NULL AUTO_INCREMENT,
  `CityName` varchar(50) NOT NULL,
  `CountryCode` int(11) DEFAULT NULL,
  PRIMARY KEY (`CityId`),
  KEY `fk_city_country` (`CountryCode`),
  CONSTRAINT `fk_city_country` FOREIGN KEY (`CountryCode`) REFERENCES `country` (`CountryCode`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `city_cricket_association`
--

DROP TABLE IF EXISTS `city_cricket_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `city_cricket_association` (
  `CCAId` int(11) NOT NULL AUTO_INCREMENT,
  `CCAName` varchar(30) NOT NULL,
  `CAId` int(11) NOT NULL,
  `CityId` int(11) NOT NULL,
  `Address` varchar(50) DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Website` varchar(30) DEFAULT NULL,
  `FBPage` varchar(40) DEFAULT NULL,
  `Twitter` varchar(30) DEFAULT NULL,
  `Email` varchar(30) DEFAULT NULL,
  `Contact` varchar(30) DEFAULT NULL,
  `Valid` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`CCAId`),
  KEY `fk_cca_city` (`CityId`),
  CONSTRAINT `fk_cca_ca` FOREIGN KEY (`CCAId`) REFERENCES `cricket_association` (`CAId`),
  CONSTRAINT `fk_cca_city` FOREIGN KEY (`CityId`) REFERENCES `city` (`CityId`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `club`
--

DROP TABLE IF EXISTS `club`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `club` (
  `ClubId` int(11) NOT NULL AUTO_INCREMENT,
  `ClubName` varchar(45) NOT NULL DEFAULT ' ',
  `President` varchar(45) DEFAULT ' ',
  `Coach` varchar(45) DEFAULT ' ',
  `Address` varchar(100) DEFAULT ' ',
  `Description` varchar(500) DEFAULT ' ',
  `AssociationId` int(10) unsigned DEFAULT NULL,
  `Valid` tinyint(1) NOT NULL DEFAULT 1,
  `Location` varchar(25) DEFAULT '33.594880, 73.051201',
  `Logo` tinyint(1) DEFAULT 0,
  `ContactNo` varchar(15) DEFAULT ' ',
  `Treasurer` varchar(45) DEFAULT ' ',
  `Secretary` varchar(45) DEFAULT ' ',
  `Registered` tinyint(1) NOT NULL DEFAULT 1,
  `ClubPassword` varchar(20) CHARACTER SET latin1 COLLATE latin1_bin DEFAULT NULL,
  `Cover` tinyint(4) NOT NULL,
  `Email` varchar(60) NOT NULL,
  `Website` varchar(60) NOT NULL,
  `FBPage` varchar(60) NOT NULL,
  `Trusted` tinyint(1) NOT NULL DEFAULT 0,
  `PresidentContact` varchar(100) DEFAULT NULL,
  `PresidentPic` int(1) NOT NULL DEFAULT 0,
  `SecretaryContact` varchar(100) DEFAULT NULL,
  `SecretaryPic` int(1) NOT NULL DEFAULT 0,
  `TreasurerContact` varchar(100) DEFAULT NULL,
  `TreasurerPic` int(1) NOT NULL DEFAULT 0,
  `ShortName` varchar(10) NOT NULL,
  `Captain` int(11) DEFAULT NULL,
  `CCA` int(11) DEFAULT NULL,
  `countryid` int(11) DEFAULT NULL,
  `cityid` int(11) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `country` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`ClubId`),
  KEY `FK_club_association` (`AssociationId`),
  FULLTEXT KEY `idx_clubname` (`ClubName`),
  CONSTRAINT `FK_club_association` FOREIGN KEY (`AssociationId`) REFERENCES `association` (`AssociationId`)
) ENGINE=InnoDB AUTO_INCREMENT=2841 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment` (
  `CommentId` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ArticleId` int(11) unsigned zerofill NOT NULL,
  `CommentBy` varchar(45) NOT NULL,
  `CommentDate` datetime NOT NULL,
  `Msg` varchar(1500) NOT NULL,
  `Visible` tinyint(1) NOT NULL DEFAULT 1,
  `email` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`CommentId`),
  KEY `idx_articleid` (`ArticleId`),
  CONSTRAINT `FK_comment_article` FOREIGN KEY (`ArticleId`) REFERENCES `article` (`ArticleId`)
) ENGINE=InnoDB AUTO_INCREMENT=5390 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `country`
--

DROP TABLE IF EXISTS `country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `country` (
  `CountryName` varchar(50) DEFAULT NULL,
  `BoardName` varchar(60) DEFAULT NULL,
  `ISOCode2` varchar(2) DEFAULT NULL,
  `ISOCode3` varchar(3) DEFAULT NULL,
  `CountryCode` int(11) NOT NULL DEFAULT 92,
  PRIMARY KEY (`CountryCode`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cricket_association`
--

DROP TABLE IF EXISTS `cricket_association`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cricket_association` (
  `CAId` int(11) NOT NULL AUTO_INCREMENT,
  `CAName` varchar(30) NOT NULL,
  `Address` varchar(50) DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Website` varchar(30) DEFAULT NULL,
  `FBPage` varchar(40) DEFAULT NULL,
  `Twitter` varchar(30) DEFAULT NULL,
  `Email` varchar(30) DEFAULT NULL,
  `Contact` varchar(30) DEFAULT NULL,
  `Valid` tinyint(4) NOT NULL DEFAULT 1,
  `CountryCode` int(11) DEFAULT NULL,
  PRIMARY KEY (`CAId`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `current_day`
--

DROP TABLE IF EXISTS `current_day`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `current_day` (
  `FinDay` date NOT NULL,
  `Current` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`FinDay`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `DepartmentId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `DepartmentName` varchar(45) NOT NULL DEFAULT ' ',
  `Description` varchar(200) DEFAULT NULL,
  `ShortName` varchar(10) NOT NULL,
  PRIMARY KEY (`DepartmentId`),
  UNIQUE KEY `DepartmentName` (`DepartmentName`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `edition`
--

DROP TABLE IF EXISTS `edition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `edition` (
  `EditionId` int(11) NOT NULL,
  `EditionName` varchar(30) NOT NULL,
  `Season` varchar(7) NOT NULL,
  PRIMARY KEY (`EditionId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `event`
--

DROP TABLE IF EXISTS `event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `event` (
  `EventId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Type` varchar(45) NOT NULL,
  `StartDate` datetime NOT NULL,
  `Detail` varchar(100) DEFAULT NULL,
  `AssociationId` int(10) unsigned DEFAULT NULL,
  `Valid` tinyint(1) NOT NULL,
  `HeldBy` varchar(40) DEFAULT NULL,
  `Status` char(1) NOT NULL DEFAULT 'A',
  `EndDate` datetime DEFAULT NULL,
  PRIMARY KEY (`EventId`),
  KEY `FK_event_association` (`AssociationId`),
  CONSTRAINT `FK_event_association` FOREIGN KEY (`AssociationId`) REFERENCES `association` (`AssociationId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fantasy_prediction`
--

DROP TABLE IF EXISTS `fantasy_prediction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasy_prediction` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TournamentId` int(11) NOT NULL,
  `MatchNo` int(11) NOT NULL,
  `FUserId` int(11) NOT NULL,
  `Prediction` int(11) NOT NULL DEFAULT 0,
  `Result` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `unq_match_user` (`MatchNo`,`FUserId`)
) ENGINE=InnoDB AUTO_INCREMENT=132 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fantasy_result`
--

DROP TABLE IF EXISTS `fantasy_result`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasy_result` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TournamentId` int(11) NOT NULL,
  `MatchNo` int(11) NOT NULL,
  `Winner` int(11) NOT NULL,
  `Total` int(7) NOT NULL,
  `MoM` int(11) NOT NULL,
  `TopScorer` int(11) NOT NULL,
  `TopWicketTaker` int(11) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fantasy_user`
--

DROP TABLE IF EXISTS `fantasy_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `fantasy_user` (
  `FUserId` int(11) NOT NULL AUTO_INCREMENT,
  `PhoneNo` varchar(15) NOT NULL,
  `FPassword` varchar(20) NOT NULL,
  `FullName` varchar(50) NOT NULL,
  `Address` varchar(80) NOT NULL,
  `DistrictId` int(11) NOT NULL,
  `Gender` enum('M','F') NOT NULL,
  `Email` varchar(50) NOT NULL,
  `AgeGroup` varchar(12) NOT NULL,
  `Incomplete` int(1) NOT NULL DEFAULT 0,
  `FBId` varchar(30) DEFAULT '0',
  PRIMARY KEY (`FUserId`),
  UNIQUE KEY `unq_phone_fantasyuser` (`PhoneNo`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `Id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Email` varchar(45) DEFAULT NULL,
  `MsgSubject` varchar(50) DEFAULT NULL,
  `Msg` varchar(300) NOT NULL,
  `Dated` datetime NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `fow`
--

DROP TABLE IF EXISTS `fow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `fow` (
  `MatchNo` int(11) NOT NULL DEFAULT 0,
  `Innings` int(11) NOT NULL DEFAULT 0,
  `Wicket` int(11) NOT NULL DEFAULT 0,
  `Overs` double DEFAULT NULL,
  `Score` int(11) DEFAULT NULL,
  `Bowler` int(11) DEFAULT NULL,
  `Batsman` int(11) DEFAULT NULL,
  `BatsmanRuns` int(11) DEFAULT NULL,
  `NewBatsman` int(11) DEFAULT NULL,
  `Fielder` int(11) DEFAULT NULL,
  `HowOut` varchar(10) DEFAULT NULL,
  `OutDetail` varchar(30) DEFAULT NULL,
  `BatsmanName` varchar(50) DEFAULT NULL,
  `NewBatsmanName` varchar(50) DEFAULT NULL,
  `FielderName` varchar(50) DEFAULT NULL,
  `BowlerName` varchar(50) DEFAULT NULL,
  `Balls` int(11) DEFAULT 0,
  PRIMARY KEY (`MatchNo`,`Innings`,`Wicket`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gallery`
--

DROP TABLE IF EXISTS `gallery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `gallery` (
  `GalleryId` int(11) NOT NULL AUTO_INCREMENT,
  `GalleryName` varchar(45) DEFAULT NULL,
  `CoverPhoto` varchar(45) DEFAULT NULL,
  `DispOrder` int(11) DEFAULT NULL,
  PRIMARY KEY (`GalleryId`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='	';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ground`
--

DROP TABLE IF EXISTS `ground`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `ground` (
  `GroundId` int(11) NOT NULL AUTO_INCREMENT,
  `GroundName` varchar(50) DEFAULT NULL,
  `Address` varchar(100) DEFAULT ' ',
  `ContactPerson` varchar(30) DEFAULT ' ',
  `ContactNo` varchar(30) DEFAULT ' ',
  `Fee` varchar(50) DEFAULT '0',
  `Status` int(11) DEFAULT 1,
  `Location` varchar(25) DEFAULT NULL,
  `AssociationId` int(10) unsigned DEFAULT NULL,
  `CityId` int(11) DEFAULT NULL,
  `CountryCode` int(11) DEFAULT NULL,
  PRIMARY KEY (`GroundId`),
  KEY `FK_ground_association` (`AssociationId`),
  KEY `CityId` (`CityId`),
  KEY `CountryCode` (`CountryCode`),
  CONSTRAINT `FK_ground_association` FOREIGN KEY (`AssociationId`) REFERENCES `association` (`AssociationId`),
  CONSTRAINT `ground_ibfk_1` FOREIGN KEY (`CityId`) REFERENCES `city` (`CityId`),
  CONSTRAINT `ground_ibfk_2` FOREIGN KEY (`CountryCode`) REFERENCES `country` (`CountryCode`)
) ENGINE=InnoDB AUTO_INCREMENT=310 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `group` (
  `GroupId` int(11) NOT NULL AUTO_INCREMENT,
  `GroupName` varchar(100) DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`GroupId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `group_screen`
--

DROP TABLE IF EXISTS `group_screen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `group_screen` (
  `ScreenId` int(11) NOT NULL,
  `GroupId` int(11) NOT NULL,
  PRIMARY KEY (`ScreenId`,`GroupId`),
  KEY `GroupId` (`GroupId`),
  CONSTRAINT `group_screen_ibfk_1` FOREIGN KEY (`ScreenId`) REFERENCES `screen` (`ScreenId`),
  CONSTRAINT `group_screen_ibfk_2` FOREIGN KEY (`GroupId`) REFERENCES `user_group` (`GroupId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `innings`
--

DROP TABLE IF EXISTS `innings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `innings` (
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `Score` int(11) DEFAULT NULL,
  `Overs` double DEFAULT NULL,
  `Byes` int(11) DEFAULT NULL,
  `LByes` int(11) DEFAULT NULL,
  `Wides` int(11) DEFAULT NULL,
  `NoBalls` int(11) DEFAULT NULL,
  `BattingTeam` int(11) DEFAULT NULL,
  `BowlingTeam` int(11) DEFAULT NULL,
  `Wickets` int(11) DEFAULT 0,
  `UpdateBy` int(11) NOT NULL,
  `UpdateTime` datetime NOT NULL,
  `BattingTeamName` varchar(50) DEFAULT NULL,
  `BowlingTeamName` varchar(50) DEFAULT NULL,
  `MatchType` varchar(1) DEFAULT 'C',
  `CurrentStrikePlayerId` int(11) DEFAULT NULL,
  `ballsInCurrentOver` int(11) DEFAULT NULL,
  `CurrentNonStrikePlayerId` int(11) DEFAULT NULL,
  `CurrentBowlerPlayerId` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`),
  KEY `FK_batting_club` (`BattingTeam`) USING BTREE,
  CONSTRAINT `FK_innings_Match` FOREIGN KEY (`MatchNo`) REFERENCES `matches` (`MatchNo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `inreport`
--

DROP TABLE IF EXISTS `inreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `inreport` (
  `ReportId` int(11) NOT NULL AUTO_INCREMENT,
  `ReportName` varchar(200) DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`ReportId`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_ball_by_ball`
--

DROP TABLE IF EXISTS `live_ball_by_ball`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_ball_by_ball` (
  `BallId` bigint(20) NOT NULL AUTO_INCREMENT,
  `ClientEventId` varchar(100) NOT NULL,
  `RefClientEventId` varchar(100) DEFAULT NULL,
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `SequenceNo` int(11) NOT NULL,
  `DeviceId` varchar(100) NOT NULL,
  `EventType` varchar(30) NOT NULL DEFAULT 'BALL',
  `Over` int(11) NOT NULL,
  `Ball` int(11) NOT NULL,
  `DisplayBall` varchar(20) DEFAULT NULL,
  `BatsmanId` int(11) DEFAULT NULL,
  `NonStrikerId` int(11) DEFAULT NULL,
  `BowlerId` int(11) DEFAULT NULL,
  `Strike` int(11) DEFAULT NULL,
  `Runs` int(11) NOT NULL DEFAULT 0,
  `Wide` int(11) NOT NULL DEFAULT 0,
  `NoBall` int(11) NOT NULL DEFAULT 0,
  `LegByes` int(11) NOT NULL DEFAULT 0,
  `Byes` int(11) NOT NULL DEFAULT 0,
  `Penalty` int(11) NOT NULL DEFAULT 0,
  `FreeHit` tinyint(1) NOT NULL DEFAULT 0,
  `Wicket` tinyint(1) NOT NULL DEFAULT 0,
  `HowOut` varchar(100) DEFAULT NULL,
  `OutPlayerId` int(11) DEFAULT NULL,
  `FielderId` int(11) DEFAULT NULL,
  `Comment` varchar(255) DEFAULT NULL,
  `BallPitch` varchar(40) DEFAULT NULL,
  `ShotPosition` varchar(20) DEFAULT NULL,
  `ShotArea` varchar(50) DEFAULT NULL,
  `ShotType` int(11) NOT NULL DEFAULT 0,
  `Inverse` tinyint(1) NOT NULL DEFAULT 0,
  `BatsmanName` varchar(100) DEFAULT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `IsDeleted` tinyint(1) NOT NULL DEFAULT 0,
  `CreatedOnDeviceAt` datetime DEFAULT NULL,
  `ModifiedOnDeviceAt` datetime DEFAULT NULL,
  `ReceivedAt` datetime NOT NULL DEFAULT current_timestamp(),
  `ProcessedAt` datetime DEFAULT NULL,
  `SyncStatus` varchar(20) NOT NULL DEFAULT 'ACCEPTED',
  PRIMARY KEY (`BallId`),
  UNIQUE KEY `uq_ball_by_ball_client_event` (`ClientEventId`),
  KEY `idx_ball_by_ball_match_innings_seq` (`MatchNo`,`Innings`,`SequenceNo`),
  KEY `idx_ball_by_ball_match_innings_over_ball` (`MatchNo`,`Innings`,`Over`,`Ball`),
  KEY `idx_ball_by_ball_ref_client_event` (`RefClientEventId`),
  KEY `idx_ball_by_ball_sync_status` (`SyncStatus`),
  KEY `idx_ball_by_ball_match` (`MatchNo`),
  KEY `idx_ball_by_ball_batsman` (`BatsmanId`),
  KEY `idx_ball_by_ball_non_striker` (`NonStrikerId`),
  KEY `idx_ball_by_ball_bowler` (`BowlerId`),
  KEY `idx_ball_by_ball_out_player` (`OutPlayerId`),
  KEY `idx_ball_by_ball_fielder` (`FielderId`)
) ENGINE=InnoDB AUTO_INCREMENT=362 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_batting_detail`
--

DROP TABLE IF EXISTS `live_batting_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_batting_detail` (
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `PlayerId` int(11) NOT NULL,
  `Runs` int(11) DEFAULT 0,
  `BallsFaced` int(11) DEFAULT 0,
  `Fours` int(11) DEFAULT 0,
  `Sixes` int(11) DEFAULT 0,
  `Singles` int(11) DEFAULT 0,
  `Doubles` int(11) DEFAULT 0,
  `Threes` int(11) DEFAULT 0,
  `Dots` int(11) DEFAULT 0,
  `NotOut` tinyint(1) DEFAULT NULL,
  `HowOut` varchar(20) DEFAULT NULL,
  `OutDetail` varchar(50) DEFAULT NULL,
  `Bowler` int(11) DEFAULT NULL,
  `Fielder` int(11) DEFAULT NULL,
  `Position` int(11) DEFAULT 0,
  `UpdateBy` int(11) NOT NULL,
  `LastUpdated` datetime NOT NULL,
  `BatsmanName` varchar(100) DEFAULT NULL,
  `FielderName` varchar(100) DEFAULT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `TeamId` int(11) DEFAULT NULL,
  `TeamName` varchar(100) DEFAULT NULL,
  `MatchType` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`,`PlayerId`),
  KEY `batting_player_fkey` (`PlayerId`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_bowling_detail`
--

DROP TABLE IF EXISTS `live_bowling_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_bowling_detail` (
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `PlayerId` int(11) NOT NULL,
  `Overs` double DEFAULT 0,
  `Maiden` int(11) DEFAULT 0,
  `Runs` int(11) DEFAULT 0,
  `Wickets` int(11) DEFAULT 0,
  `Wides` int(11) DEFAULT 0,
  `NoBalls` int(11) DEFAULT 0,
  `TeamId` int(11) DEFAULT NULL,
  `TeamName` varchar(45) NOT NULL,
  `Position` int(11) DEFAULT 0,
  `Current` int(11) NOT NULL,
  `UpdateBy` int(11) NOT NULL,
  `LastUpdate` datetime NOT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `MatchType` varchar(1) DEFAULT NULL,
  `Balls` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`,`PlayerId`),
  KEY `bowling_player_fkey` (`PlayerId`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_fow`
--

DROP TABLE IF EXISTS `live_fow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_fow` (
  `MatchNo` int(11) NOT NULL DEFAULT 0,
  `Innings` int(11) NOT NULL DEFAULT 0,
  `Wicket` int(11) NOT NULL DEFAULT 0,
  `Overs` double DEFAULT NULL,
  `Score` int(11) DEFAULT NULL,
  `Bowler` int(11) DEFAULT NULL,
  `Batsman` int(11) DEFAULT NULL,
  `BatsmanRuns` int(11) DEFAULT NULL,
  `NewBatsman` int(11) DEFAULT NULL,
  `Fielder` int(11) DEFAULT NULL,
  `HowOut` varchar(10) DEFAULT NULL,
  `OutDetail` varchar(30) DEFAULT NULL,
  `BatsmanName` varchar(50) DEFAULT NULL,
  `NewBatsmanName` varchar(50) DEFAULT NULL,
  `FielderName` varchar(50) DEFAULT NULL,
  `BowlerName` varchar(50) DEFAULT NULL,
  `Balls` int(11) DEFAULT 0,
  PRIMARY KEY (`MatchNo`,`Innings`,`Wicket`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_innings`
--

DROP TABLE IF EXISTS `live_innings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_innings` (
  `MatchNo` int(11) NOT NULL,
  `Innings` int(11) NOT NULL,
  `Score` int(11) DEFAULT NULL,
  `Overs` double DEFAULT NULL,
  `Byes` int(11) DEFAULT NULL,
  `LByes` int(11) DEFAULT NULL,
  `Wides` int(11) DEFAULT NULL,
  `NoBalls` int(11) DEFAULT NULL,
  `BattingTeam` int(11) DEFAULT NULL,
  `BowlingTeam` int(11) DEFAULT NULL,
  `Wickets` int(11) DEFAULT 0,
  `UpdateBy` int(11) NOT NULL,
  `UpdateTime` timestamp NULL DEFAULT current_timestamp(),
  `BattingTeamName` varchar(50) DEFAULT NULL,
  `BowlingTeamName` varchar(50) DEFAULT NULL,
  `matchtype` varchar(20) DEFAULT NULL,
  `LastUpdated` timestamp NULL DEFAULT current_timestamp(),
  `CurrentStrikePlayerId` int(11) DEFAULT NULL,
  `ballsInCurrentOver` int(11) DEFAULT NULL,
  `CurrentNonStrikePlayerId` int(11) DEFAULT NULL,
  `CurrentBowlerPlayerId` int(11) DEFAULT NULL,
  `IsCompleted` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`),
  KEY `FK_batting_club` (`BattingTeam`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_match_over`
--

DROP TABLE IF EXISTS `live_match_over`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_match_over` (
  `MatchNo` int(11) NOT NULL DEFAULT 0,
  `Innings` int(11) NOT NULL DEFAULT 0,
  `Over` double NOT NULL DEFAULT 0,
  `Score` int(11) DEFAULT 0,
  `Wicket` int(11) DEFAULT 0,
  `Bowler` int(11) DEFAULT 0,
  `Striker` int(11) DEFAULT 0,
  `NonStriker` int(11) DEFAULT 0,
  `StrikerRuns` int(11) DEFAULT 0,
  `StrikerBalls` int(11) NOT NULL DEFAULT 0,
  `NonStrikerRuns` int(11) DEFAULT 0,
  `NonStrikerBalls` int(11) NOT NULL DEFAULT 0,
  `RunsInOver` int(11) DEFAULT 0,
  `WicketsInOver` int(11) DEFAULT 0,
  `Wides` int(11) DEFAULT 0,
  `NoBalls` int(11) DEFAULT 0,
  `Byes` int(11) DEFAULT 0,
  `LByes` int(11) DEFAULT 0,
  `EndOfOver` int(11) NOT NULL,
  `StrikerName` varchar(100) DEFAULT NULL,
  `NonStrikerName` varchar(100) DEFAULT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `BowlerOver` double DEFAULT NULL,
  `Maiden` int(11) DEFAULT NULL,
  `BowlerRuns` int(11) DEFAULT NULL,
  `BowlerWicket` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`,`Over`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_match_squad`
--

DROP TABLE IF EXISTS `live_match_squad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_match_squad` (
  `TeamId` int(11) NOT NULL DEFAULT 0,
  `PlayerId` int(11) NOT NULL DEFAULT 0,
  `MatchNo` int(11) NOT NULL,
  `ShirtNo` int(11) DEFAULT NULL,
  `TeamType` varchar(1) DEFAULT 'C',
  PRIMARY KEY (`TeamId`,`PlayerId`,`MatchNo`) USING BTREE,
  UNIQUE KEY `fk_match_squad` (`PlayerId`,`MatchNo`),
  KEY `fk_matchsquad_match` (`MatchNo`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `live_matches`
--

DROP TABLE IF EXISTS `live_matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `live_matches` (
  `MatchNo` int(11) NOT NULL,
  `Season` varchar(7) DEFAULT NULL,
  `GroundId` int(11) DEFAULT NULL,
  `Dated` datetime DEFAULT NULL,
  `Winner` int(10) unsigned DEFAULT NULL,
  `ResultDetail` varchar(150) DEFAULT NULL,
  `Overs` int(11) DEFAULT NULL,
  `Status` varchar(1) DEFAULT 'S',
  `Team1` int(10) NOT NULL,
  `Team2` int(10) NOT NULL,
  `Type` varchar(20) NOT NULL DEFAULT 'Friendly Match',
  `TournamentId` int(10) unsigned DEFAULT NULL,
  `RoundId` int(11) NOT NULL DEFAULT 0,
  `Format` varchar(20) NOT NULL DEFAULT 'One Day',
  `Level` varchar(10) DEFAULT ' ',
  `Live` tinyint(1) NOT NULL DEFAULT 0,
  `RunnerUP` int(10) DEFAULT NULL,
  `Summary` varchar(3500) DEFAULT NULL,
  `ManOfMatch` int(10) DEFAULT NULL,
  `Toss` int(10) DEFAULT NULL,
  `ScoreCard` int(11) NOT NULL,
  `CurrentInn` int(11) NOT NULL,
  `Commentary` int(11) NOT NULL DEFAULT 0,
  `Official` int(11) NOT NULL DEFAULT 0,
  `GroupId` int(11) DEFAULT NULL,
  `Stage` varchar(15) NOT NULL DEFAULT 'CF',
  `Scorer` varchar(45) DEFAULT NULL,
  `Umpires` varchar(80) NOT NULL,
  `Refree` varchar(45) NOT NULL,
  `CoverPhoto` varchar(50) DEFAULT NULL,
  `TagLine` varchar(60) NOT NULL,
  `TournamentGroup` varchar(30) DEFAULT NULL,
  `PredictionStart` int(11) NOT NULL DEFAULT 0,
  `UpdateBy` int(11) NOT NULL,
  `UpdateTime` datetime NOT NULL,
  `Team1RR` double NOT NULL DEFAULT 0,
  `Team2RR` double NOT NULL DEFAULT 0,
  `ScorerId` int(11) DEFAULT 0,
  `LiveType` varchar(1) DEFAULT NULL,
  `ResultType` enum('WinLoss','Tie','Draw','No Result','Abandoned','Awarded','Conceded') NOT NULL DEFAULT 'WinLoss',
  `IncludeNetRR` int(1) NOT NULL DEFAULT 1,
  `CountryCode` int(11) DEFAULT NULL,
  `Club` tinyint(1) DEFAULT 0,
  `Team` tinyint(1) DEFAULT 1,
  `City` int(11) DEFAULT NULL,
  `MatchLevel` varchar(20) DEFAULT NULL,
  `ICCRecognised` tinyint(1) DEFAULT 0,
  `ICCEvent` tinyint(1) DEFAULT 0,
  `EntryStatus` varchar(1) DEFAULT 'S',
  `Team1Name` varchar(45) DEFAULT NULL,
  `Team2Name` varchar(45) DEFAULT NULL,
  `WinnerName` varchar(45) DEFAULT NULL,
  `RunnerupName` varchar(45) DEFAULT NULL,
  `CountryName` varchar(50) DEFAULT NULL,
  `CityName` varchar(50) DEFAULT NULL,
  `LastUpdated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`MatchNo`),
  KEY `match_ground_fkey` (`GroundId`) USING BTREE,
  KEY `match_season_fkey` (`Season`) USING BTREE,
  KEY `FK_matches_player` (`ManOfMatch`),
  KEY `fk_matches_scorer` (`ScorerId`),
  KEY `fk_matches_city` (`City`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `livescore`
--

DROP TABLE IF EXISTS `livescore`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `livescore` (
  `Id` datetime NOT NULL,
  `Team1` varchar(45) NOT NULL,
  `Team2` varchar(45) DEFAULT NULL,
  `Score1` varchar(100) DEFAULT NULL,
  `Bowl1` varchar(100) DEFAULT NULL,
  `Score2` varchar(100) DEFAULT NULL,
  `Bowl2` varchar(100) DEFAULT NULL,
  `Result` varchar(45) DEFAULT NULL,
  `Tournament` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `match_comments`
--

DROP TABLE IF EXISTS `match_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `match_comments` (
  `CommentId` int(11) NOT NULL AUTO_INCREMENT,
  `MatchNo` int(11) DEFAULT NULL,
  `Innings` int(11) DEFAULT NULL,
  `Over` double DEFAULT NULL,
  `Sender` varchar(30) DEFAULT NULL,
  `Comments` varchar(300) DEFAULT NULL,
  `IsAdmin` int(1) DEFAULT NULL,
  `IsApproved` int(1) DEFAULT NULL,
  `Include` int(1) DEFAULT 0,
  PRIMARY KEY (`CommentId`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `match_over`
--

DROP TABLE IF EXISTS `match_over`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `match_over` (
  `MatchNo` int(11) NOT NULL DEFAULT 0,
  `Innings` int(11) NOT NULL DEFAULT 0,
  `Over` double NOT NULL DEFAULT 0,
  `Score` int(11) DEFAULT 0,
  `Wicket` int(11) DEFAULT 0,
  `Bowler` int(11) DEFAULT 0,
  `Striker` int(11) DEFAULT 0,
  `NonStriker` int(11) DEFAULT 0,
  `StrikerRuns` int(11) DEFAULT 0,
  `StrikerBalls` int(11) NOT NULL DEFAULT 0,
  `NonStrikerRuns` int(11) DEFAULT 0,
  `NonStrikerBalls` int(11) NOT NULL DEFAULT 0,
  `RunsInOver` int(11) DEFAULT 0,
  `WicketsInOver` int(11) DEFAULT 0,
  `Wides` int(11) DEFAULT 0,
  `NoBalls` int(11) DEFAULT 0,
  `Byes` int(11) DEFAULT 0,
  `LByes` int(11) DEFAULT 0,
  `EndOfOver` int(11) NOT NULL,
  `StrikerName` varchar(100) DEFAULT NULL,
  `NonStrikerName` varchar(100) DEFAULT NULL,
  `BowlerName` varchar(100) DEFAULT NULL,
  `BowlerOver` double DEFAULT NULL,
  `Maiden` int(11) DEFAULT NULL,
  `BowlerRuns` int(11) DEFAULT NULL,
  `BowlerWicket` int(11) DEFAULT NULL,
  PRIMARY KEY (`MatchNo`,`Innings`,`Over`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `match_squad`
--

DROP TABLE IF EXISTS `match_squad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `match_squad` (
  `TeamId` int(11) NOT NULL DEFAULT 0,
  `PlayerId` int(11) NOT NULL DEFAULT 0,
  `MatchNo` int(11) NOT NULL,
  `ShirtNo` int(11) DEFAULT NULL,
  `TeamType` varchar(1) DEFAULT 'C',
  PRIMARY KEY (`TeamId`,`PlayerId`,`MatchNo`) USING BTREE,
  UNIQUE KEY `fk_match_squad` (`PlayerId`,`MatchNo`),
  KEY `fk_matchsquad_match` (`MatchNo`),
  CONSTRAINT `fk_matchsquad_match` FOREIGN KEY (`MatchNo`) REFERENCES `matches` (`MatchNo`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches`
--

DROP TABLE IF EXISTS `matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches` (
  `MatchNo` int(11) NOT NULL,
  `Season` varchar(7) DEFAULT NULL,
  `GroundId` int(11) DEFAULT NULL,
  `Dated` datetime DEFAULT NULL,
  `Winner` int(10) unsigned DEFAULT NULL,
  `ResultDetail` varchar(150) DEFAULT NULL,
  `Overs` int(11) DEFAULT NULL,
  `Status` varchar(1) DEFAULT 'S',
  `Team1` int(10) NOT NULL,
  `Team2` int(10) NOT NULL,
  `Type` varchar(20) NOT NULL DEFAULT 'Friendly Match',
  `TournamentId` int(10) unsigned DEFAULT NULL,
  `RoundId` int(11) NOT NULL DEFAULT 0,
  `Format` varchar(20) NOT NULL DEFAULT 'One Day',
  `Level` varchar(10) DEFAULT ' ',
  `Live` tinyint(1) NOT NULL DEFAULT 0,
  `RunnerUP` int(10) DEFAULT NULL,
  `Summary` varchar(3500) DEFAULT NULL,
  `ManOfMatch` int(10) DEFAULT NULL,
  `Toss` int(10) DEFAULT NULL,
  `ScoreCard` int(11) NOT NULL,
  `CurrentInn` int(11) NOT NULL,
  `Commentary` int(11) NOT NULL DEFAULT 0,
  `Official` int(11) NOT NULL DEFAULT 0,
  `GroupId` int(11) DEFAULT NULL,
  `Stage` varchar(15) NOT NULL DEFAULT 'CF',
  `Scorer` varchar(45) DEFAULT NULL,
  `Umpires` varchar(80) NOT NULL,
  `Refree` varchar(45) NOT NULL,
  `CoverPhoto` varchar(50) DEFAULT NULL,
  `TagLine` varchar(60) NOT NULL,
  `TournamentGroup` varchar(30) DEFAULT NULL,
  `PredictionStart` int(11) NOT NULL DEFAULT 0,
  `UpdateBy` int(11) NOT NULL,
  `UpdateTime` datetime NOT NULL,
  `Team1RR` double NOT NULL DEFAULT 0,
  `Team2RR` double NOT NULL DEFAULT 0,
  `ScorerId` int(11) DEFAULT 0,
  `LiveType` varchar(1) DEFAULT NULL,
  `ResultType` enum('WinLoss','Tie','Draw','No Result','Abandoned','Awarded','Conceded') NOT NULL DEFAULT 'WinLoss',
  `IncludeNetRR` int(1) NOT NULL DEFAULT 1,
  `CountryCode` int(11) DEFAULT NULL,
  `Club` tinyint(1) DEFAULT 0,
  `Team` tinyint(1) DEFAULT 1,
  `City` int(11) DEFAULT NULL,
  `MatchLevel` varchar(20) DEFAULT NULL,
  `ICCRecognised` tinyint(1) DEFAULT 0,
  `ICCEvent` tinyint(1) DEFAULT 0,
  `EntryStatus` varchar(1) DEFAULT 'S',
  `Team1Name` varchar(45) DEFAULT NULL,
  `Team2Name` varchar(45) DEFAULT NULL,
  `WinnerName` varchar(45) DEFAULT NULL,
  `RunnerupName` varchar(45) DEFAULT NULL,
  `CountryName` varchar(50) DEFAULT NULL,
  `CityName` varchar(50) DEFAULT NULL,
  `LastUpdated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`MatchNo`),
  KEY `match_ground_fkey` (`GroundId`) USING BTREE,
  KEY `match_season_fkey` (`Season`) USING BTREE,
  KEY `FK_matches_player` (`ManOfMatch`),
  KEY `fk_matches_scorer` (`ScorerId`),
  KEY `fk_matches_city` (`City`),
  CONSTRAINT `FK_matches_ground` FOREIGN KEY (`GroundId`) REFERENCES `ground` (`GroundId`),
  CONSTRAINT `FK_matches_season` FOREIGN KEY (`Season`) REFERENCES `season` (`Season`),
  CONSTRAINT `fk_matches_city` FOREIGN KEY (`City`) REFERENCES `city` (`CityId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `media_item`
--

DROP TABLE IF EXISTS `media_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_item` (
  `ItemId` int(11) NOT NULL AUTO_INCREMENT,
  `Dated` datetime DEFAULT NULL,
  `Heading` varchar(100) DEFAULT NULL,
  `src` varchar(50) DEFAULT NULL,
  `GroupId` int(11) DEFAULT NULL,
  `Height` int(11) NOT NULL,
  `Width` int(11) NOT NULL,
  PRIMARY KEY (`ItemId`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `news`
--

DROP TABLE IF EXISTS `news`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `news` (
  `NewsId` int(11) NOT NULL AUTO_INCREMENT,
  `RefId` int(11) DEFAULT NULL,
  `Dated` datetime DEFAULT NULL,
  `Type` varchar(1) DEFAULT 'C',
  `Urdu` tinyint(1) DEFAULT NULL,
  `NewsText` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`NewsId`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `object_pics`
--

DROP TABLE IF EXISTS `object_pics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `object_pics` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ObjectType` varchar(30) NOT NULL,
  `ObjectId` int(11) NOT NULL,
  `Caption` varchar(80) NOT NULL,
  `ImagePath` varchar(50) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `idx_type_objid` (`ObjectType`,`ObjectId`)
) ENGINE=MyISAM AUTO_INCREMENT=135 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `offer`
--

DROP TABLE IF EXISTS `offer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `offer` (
  `OfferId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ClubId` int(11) NOT NULL,
  `OfferDate` datetime NOT NULL,
  `Ground` varchar(70) NOT NULL,
  `Remove` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`OfferId`),
  KEY `FK_offer_Club` (`ClubId`),
  CONSTRAINT `FK_offer_Club` FOREIGN KEY (`ClubId`) REFERENCES `club` (`ClubId`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `official`
--

DROP TABLE IF EXISTS `official`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `official` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Type` varchar(1) NOT NULL,
  `Designation` varchar(50) NOT NULL,
  `Name` varchar(80) NOT NULL,
  `ContactDetail` varchar(100) DEFAULT NULL,
  `RefId` int(11) NOT NULL,
  `Pic` int(1) NOT NULL,
  `Priority` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`Id`),
  KEY `Id` (`Id`,`Type`)
) ENGINE=InnoDB AUTO_INCREMENT=3887 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `outreport`
--

DROP TABLE IF EXISTS `outreport`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `outreport` (
  `ReportId` int(11) NOT NULL AUTO_INCREMENT,
  `ReportName` varchar(200) DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  `FileNameFilter` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`ReportId`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `outreport_data`
--

DROP TABLE IF EXISTS `outreport_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `outreport_data` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `RowNumber` int(11) DEFAULT NULL,
  `ReportDate` date DEFAULT NULL,
  `HeadId` int(11) DEFAULT NULL,
  `HeadName` varchar(80) DEFAULT NULL,
  `Actual` int(11) DEFAULT NULL,
  `Budget` int(11) DEFAULT NULL,
  `LY` int(11) DEFAULT NULL,
  `MTDActual` int(11) DEFAULT NULL,
  `MTDBudget` int(11) DEFAULT NULL,
  `MTDLY` int(11) DEFAULT NULL,
  `YTDActual` int(11) DEFAULT NULL,
  `YTDBudget` int(11) DEFAULT NULL,
  `YTDLY` int(11) DEFAULT NULL,
  `SectionName` varchar(255) DEFAULT NULL,
  `SectionId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1686 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `photo`
--

DROP TABLE IF EXISTS `photo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `photo` (
  `PhotoId` int(11) NOT NULL AUTO_INCREMENT,
  `Caption` varchar(250) DEFAULT NULL,
  `GalleryId` int(11) DEFAULT NULL,
  `Path` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`PhotoId`),
  KEY `fk_photo_gallery_idx` (`GalleryId`),
  CONSTRAINT `fk_photo_gallery` FOREIGN KEY (`GalleryId`) REFERENCES `gallery` (`GalleryId`) ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=901 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='					';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `player` (
  `PlayerId` int(11) NOT NULL AUTO_INCREMENT,
  `FullName` varchar(100) DEFAULT ' ',
  `DOB` date DEFAULT '0000-00-00',
  `MajorTeams` varchar(100) DEFAULT ' ',
  `BattingStyle` varchar(50) DEFAULT ' ',
  `BowlingStyle` varchar(50) DEFAULT ' ',
  `Image` tinyint(1) NOT NULL DEFAULT 0,
  `ClubId` int(11) NOT NULL,
  `Status` tinyint(1) DEFAULT 1,
  `PlayingRole` varchar(30) DEFAULT ' ',
  `Registered` tinyint(1) NOT NULL DEFAULT 1,
  `FBId` varchar(45) NOT NULL,
  `Height` int(11) DEFAULT NULL,
  `Weight` int(11) DEFAULT NULL,
  `TwitterId` varchar(45) DEFAULT NULL,
  `ShortName` varchar(10) NOT NULL,
  `FatherName` varchar(80) NOT NULL,
  `CNIC` varchar(20) DEFAULT NULL,
  `Domicile` varchar(50) DEFAULT NULL,
  `Qualification` varchar(20) DEFAULT NULL,
  `PresentAddress` varchar(100) DEFAULT NULL,
  `PermanentAddress` varchar(100) DEFAULT NULL,
  `PHoneNo` varchar(20) DEFAULT NULL,
  `CityId` int(11) DEFAULT NULL,
  `CountryId` int(11) DEFAULT NULL,
  `City` varchar(50) DEFAULT NULL,
  `Country` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`PlayerId`),
  KEY `FK_player_club` (`ClubId`),
  KEY `idx_player_name` (`FullName`),
  CONSTRAINT `FK_player_club` FOREIGN KEY (`ClubId`) REFERENCES `club` (`ClubId`)
) ENGINE=InnoDB AUTO_INCREMENT=18956 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `player_follower`
--

DROP TABLE IF EXISTS `player_follower`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_follower` (
  `PlayerId` int(11) NOT NULL,
  `FUserId` int(11) NOT NULL,
  `FollowOn` datetime NOT NULL,
  PRIMARY KEY (`PlayerId`,`FUserId`),
  KEY `fk_playerfollower_follower_idx` (`FUserId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `point_table`
--

DROP TABLE IF EXISTS `point_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `point_table` (
  `TournamentId` int(11) NOT NULL,
  `Type` varchar(1) NOT NULL,
  `Groupe` varchar(30) NOT NULL,
  `Team` int(11) NOT NULL,
  `TeamName` varchar(45) NOT NULL,
  `Played` int(11) NOT NULL DEFAULT 0,
  `Won` int(11) NOT NULL DEFAULT 0,
  `Lost` int(11) NOT NULL DEFAULT 0,
  `Draw` int(11) NOT NULL DEFAULT 0,
  `Tie` int(11) NOT NULL DEFAULT 0,
  `Abondoned` int(11) NOT NULL DEFAULT 0,
  `WicketsLost` int(11) NOT NULL DEFAULT 0,
  `WicketsTaken` int(11) NOT NULL DEFAULT 0,
  `RunsFor` int(11) NOT NULL DEFAULT 0,
  `RunsAgainst` int(11) NOT NULL DEFAULT 0,
  `Points` int(11) NOT NULL DEFAULT 0,
  `BonusPoints` int(11) NOT NULL DEFAULT 0,
  `RunRate` double NOT NULL DEFAULT 0,
  `NetRunRate` double NOT NULL DEFAULT 0,
  PRIMARY KEY (`TournamentId`,`Groupe`,`Team`),
  UNIQUE KEY `TournamentId` (`TournamentId`,`Groupe`,`Team`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `points`
--

DROP TABLE IF EXISTS `points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `points` (
  `TournamentId` int(10) unsigned NOT NULL,
  `RoundId` int(11) NOT NULL,
  `TeamId` int(11) NOT NULL,
  `Played` int(11) NOT NULL,
  `Won` int(11) NOT NULL,
  `Lost` int(11) NOT NULL,
  `Tie` int(11) NOT NULL,
  `Draw` int(11) NOT NULL,
  `Abondoned` int(11) NOT NULL,
  `Points` int(11) NOT NULL,
  `RunsFor` int(11) NOT NULL,
  `RunsAgainst` int(11) NOT NULL,
  `WicketTaken` int(11) NOT NULL,
  `WicketsLost` int(11) NOT NULL,
  `RunRate` double NOT NULL,
  `NetRunRate` double NOT NULL,
  KEY `fk_points_roundteam` (`TournamentId`,`RoundId`,`TeamId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts` (
  `PostId` int(11) NOT NULL AUTO_INCREMENT,
  `Dated` datetime DEFAULT NULL,
  `Comments` varchar(200) DEFAULT NULL,
  `URL` varchar(80) DEFAULT NULL,
  `PostImg` varchar(80) DEFAULT NULL,
  `Visible` varchar(1) DEFAULT '1',
  PRIMARY KEY (`PostId`)
) ENGINE=InnoDB AUTO_INCREMENT=42850 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `province`
--

DROP TABLE IF EXISTS `province`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `province` (
  `ProvinceId` int(11) NOT NULL AUTO_INCREMENT,
  `ProvinceName` varchar(30) NOT NULL,
  `Description` varchar(50) NOT NULL,
  `ShortName` varchar(10) NOT NULL,
  PRIMARY KEY (`ProvinceId`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `region`
--

DROP TABLE IF EXISTS `region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `region` (
  `RegionId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `RegionName` varchar(45) NOT NULL DEFAULT ' ',
  `President` varchar(45) DEFAULT ' ',
  `Secretary` varchar(45) DEFAULT ' ',
  `Valid` tinyint(1) NOT NULL DEFAULT 1,
  `Treasurer` varchar(45) DEFAULT ' ',
  `PresidentContact` varchar(100) DEFAULT NULL,
  `PresidentPic` int(1) NOT NULL DEFAULT 0,
  `SecretaryContact` varchar(100) DEFAULT NULL,
  `SecretaryPic` int(1) NOT NULL DEFAULT 0,
  `TreasurerContact` varchar(100) DEFAULT NULL,
  `TreasurerPic` int(1) NOT NULL DEFAULT 0,
  `ShortName` varchar(10) NOT NULL,
  PRIMARY KEY (`RegionId`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `round_team`
--

DROP TABLE IF EXISTS `round_team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `round_team` (
  `RoundTeamId` int(11) NOT NULL AUTO_INCREMENT,
  `TournamentId` int(10) unsigned NOT NULL,
  `RoundId` int(11) NOT NULL,
  `TeamId` int(11) NOT NULL,
  `TeamName` varchar(80) DEFAULT NULL,
  `Played` int(11) NOT NULL DEFAULT 0,
  `Won` int(11) NOT NULL DEFAULT 0,
  `Lost` int(11) NOT NULL DEFAULT 0,
  `Tie` int(11) NOT NULL DEFAULT 0,
  `Draw` int(11) NOT NULL DEFAULT 0,
  `NoResult` int(11) NOT NULL DEFAULT 0,
  `Abandoned` int(11) NOT NULL DEFAULT 0,
  `Bonus` int(11) NOT NULL DEFAULT 0,
  `Points` int(11) NOT NULL DEFAULT 0,
  `RunsFor` int(11) NOT NULL DEFAULT 0,
  `RunsAgainst` int(11) NOT NULL DEFAULT 0,
  `OversPlayed` double NOT NULL DEFAULT 0,
  `OversBowled` double NOT NULL DEFAULT 0,
  `RunRate` double NOT NULL DEFAULT 0,
  `NetRunRate` double NOT NULL DEFAULT 0,
  PRIMARY KEY (`RoundTeamId`),
  UNIQUE KEY `idx_tournamenroundteam` (`TournamentId`,`RoundId`,`TeamId`),
  KEY `fk_roundteam_round` (`RoundId`)
) ENGINE=InnoDB AUTO_INCREMENT=328 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scorer`
--

DROP TABLE IF EXISTS `scorer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scorer` (
  `ScorerId` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(100) NOT NULL,
  `UserPassword` varchar(255) NOT NULL,
  `ScorerType` varchar(50) DEFAULT NULL,
  `LastUpdated` datetime DEFAULT NULL,
  `FullName` varchar(150) DEFAULT NULL,
  `PhoneNo` varchar(20) DEFAULT NULL,
  `Email` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`ScorerId`),
  UNIQUE KEY `UserName` (`UserName`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scorer_setup_sync_event`
--

DROP TABLE IF EXISTS `scorer_setup_sync_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scorer_setup_sync_event` (
  `ClientEventId` varchar(191) NOT NULL,
  `MatchNo` int(11) NOT NULL,
  `DeviceId` varchar(191) NOT NULL,
  `EntityType` varchar(50) NOT NULL,
  `OperationType` varchar(50) NOT NULL,
  `CreatedAt` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ClientEventId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scorer_tournament`
--

DROP TABLE IF EXISTS `scorer_tournament`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `scorer_tournament` (
  `ScorerId` int(11) NOT NULL,
  `TournamentId` int(11) unsigned NOT NULL,
  PRIMARY KEY (`ScorerId`,`TournamentId`),
  KEY `TournamentId` (`TournamentId`),
  CONSTRAINT `scorer_tournament_ibfk_1` FOREIGN KEY (`ScorerId`) REFERENCES `scorer` (`ScorerId`),
  CONSTRAINT `scorer_tournament_ibfk_2` FOREIGN KEY (`TournamentId`) REFERENCES `tournament` (`TournamentId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `screen`
--

DROP TABLE IF EXISTS `screen`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `screen` (
  `ScreenId` int(11) NOT NULL AUTO_INCREMENT,
  `ScreenName` varchar(50) DEFAULT NULL,
  `URL` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ScreenId`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `season`
--

DROP TABLE IF EXISTS `season`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `season` (
  `Season` varchar(7) NOT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Current` varchar(1) DEFAULT '0',
  PRIMARY KEY (`Season`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `section`
--

DROP TABLE IF EXISTS `section`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `section` (
  `SectionId` int(11) NOT NULL AUTO_INCREMENT,
  `SectionName` varchar(100) DEFAULT NULL,
  `Header` tinyint(1) DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  `ReportId` int(11) DEFAULT NULL,
  `summary` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`SectionId`),
  KEY `fk_section_outrep` (`ReportId`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `section_head`
--

DROP TABLE IF EXISTS `section_head`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `section_head` (
  `HeadId` int(11) NOT NULL AUTO_INCREMENT,
  `RowNo` int(11) DEFAULT NULL,
  `HeadName` varchar(100) DEFAULT NULL,
  `ValueType` varchar(20) DEFAULT 'Value',
  `ValueReport` varchar(20) DEFAULT 'InReport',
  `CellValue` varchar(80) DEFAULT NULL,
  `SectionId` int(11) DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  `ReportId` int(11) DEFAULT NULL,
  PRIMARY KEY (`HeadId`),
  KEY `fk_sectionhead_section` (`SectionId`)
) ENGINE=InnoDB AUTO_INCREMENT=116 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `squad`
--

DROP TABLE IF EXISTS `squad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `squad` (
  `TeamId` int(11) NOT NULL DEFAULT 0,
  `PlayerId` int(11) NOT NULL DEFAULT 0,
  `TournamentId` int(11) unsigned NOT NULL,
  PRIMARY KEY (`TeamId`,`PlayerId`,`TournamentId`) USING BTREE,
  UNIQUE KEY `PlayerId_2` (`PlayerId`,`TournamentId`),
  KEY `fk_squad_tournament` (`TournamentId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sw_user`
--

DROP TABLE IF EXISTS `sw_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `sw_user` (
  `UserId` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(100) DEFAULT NULL,
  `UserPassword` varchar(255) DEFAULT NULL,
  `Valid` tinyint(1) DEFAULT 1,
  `GroupId` int(11) DEFAULT NULL,
  PRIMARY KEY (`UserId`),
  UNIQUE KEY `UserName` (`UserName`),
  KEY `fk_user_group` (`GroupId`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `TagId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TagName` varchar(50) NOT NULL,
  `Slug` varchar(60) NOT NULL,
  `CreatedAt` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`TagId`),
  UNIQUE KEY `TagName` (`TagName`),
  UNIQUE KEY `Slug` (`Slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `team`
--

DROP TABLE IF EXISTS `team`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `team` (
  `TeamId` int(11) NOT NULL AUTO_INCREMENT,
  `TeamName` varchar(50) DEFAULT NULL,
  `Level` varchar(30) DEFAULT NULL,
  `TournamentId` int(11) DEFAULT NULL,
  `DistrictId` int(11) DEFAULT NULL,
  `RegionId` int(11) DEFAULT NULL,
  `DepartmentId` int(11) DEFAULT NULL,
  `Valid` int(11) DEFAULT NULL,
  `Format` varchar(20) DEFAULT NULL,
  `Coach` varchar(30) DEFAULT NULL,
  `Manager` varchar(255) DEFAULT NULL,
  `Captain` int(11) DEFAULT NULL,
  `Season` varchar(7) DEFAULT NULL,
  `Logo` tinyint(1) NOT NULL DEFAULT 0,
  `ProvinceId` int(11) DEFAULT NULL,
  `ShortName` varchar(10) NOT NULL,
  `Stage` varchar(15) DEFAULT NULL,
  `ParentId` int(11) NOT NULL DEFAULT 0,
  `EditionId` int(11) DEFAULT NULL,
  `LastUpdated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`TeamId`)
) ENGINE=InnoDB AUTO_INCREMENT=1004 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `temp`
--

DROP TABLE IF EXISTS `temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `temp` (
  `ArticleId` int(11) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) DEFAULT NULL,
  `Heading` varchar(400) DEFAULT NULL,
  `Writer` varchar(50) DEFAULT NULL,
  `Dated` datetime DEFAULT NULL,
  `Content` mediumtext DEFAULT NULL,
  `Image` varchar(80) DEFAULT NULL,
  `Caption` longtext DEFAULT NULL,
  `Status` tinyint(1) DEFAULT 1,
  `OrderNo` int(11) NOT NULL,
  `Urdu` tinyint(1) NOT NULL DEFAULT 0,
  `CreatedBy` int(11) DEFAULT NULL,
  `UpdatedBy` int(11) DEFAULT NULL,
  `CreatedAt` datetime DEFAULT NULL,
  `UpdatedAt` datetime DEFAULT NULL,
  PRIMARY KEY (`ArticleId`)
) ENGINE=InnoDB AUTO_INCREMENT=2943 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `test_table`
--

DROP TABLE IF EXISTS `test_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_table` (
  `id` int(11) DEFAULT NULL,
  `title` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `heading` varchar(400) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `content` text CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `caption` varchar(200) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournament`
--

DROP TABLE IF EXISTS `tournament`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournament` (
  `TournamentId` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Name` varchar(80) NOT NULL DEFAULT ' ',
  `Format` varchar(45) NOT NULL DEFAULT ' ',
  `StartDate` datetime DEFAULT NULL,
  `Detail` varchar(100) DEFAULT ' ',
  `AssociationId` int(10) unsigned DEFAULT NULL,
  `Valid` tinyint(1) NOT NULL DEFAULT 1,
  `Winner` int(10) unsigned DEFAULT NULL,
  `RunnerUp` int(10) unsigned DEFAULT NULL,
  `HeldBy` varchar(40) DEFAULT ' ',
  `Status` char(1) NOT NULL DEFAULT 'A',
  `EndDate` datetime DEFAULT NULL,
  `Season` varchar(10) NOT NULL,
  `Level` varchar(10) NOT NULL,
  `Type` varchar(1) NOT NULL,
  `WinPoint` int(11) NOT NULL,
  `DrawPoint` int(11) NOT NULL,
  `PredictionStart` int(11) NOT NULL DEFAULT 0,
  `AutoCalculate` int(1) NOT NULL DEFAULT 1,
  `UserPassword` varchar(20) NOT NULL,
  `Live` tinyint(1) NOT NULL DEFAULT 0,
  `OrganizerType` varchar(8) NOT NULL,
  `OrganizedBy` int(11) NOT NULL DEFAULT 0,
  `Stage` varchar(15) NOT NULL,
  `CountryName` varchar(45) DEFAULT NULL,
  `CountryCode` int(11) DEFAULT NULL,
  `City` int(11) DEFAULT NULL,
  `CityName` varchar(50) DEFAULT NULL,
  `LastUpdated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`TournamentId`),
  KEY `FK_tournament_association` (`AssociationId`),
  KEY `FK_tournament_season` (`Season`),
  KEY `AssociationId` (`AssociationId`),
  KEY `FK_CountryCode` (`CountryCode`)
) ENGINE=InnoDB AUTO_INCREMENT=193 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournament_club`
--

DROP TABLE IF EXISTS `tournament_club`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournament_club` (
  `TournamentId` int(11) unsigned NOT NULL,
  `ClubId` int(11) NOT NULL,
  PRIMARY KEY (`TournamentId`,`ClubId`),
  KEY `TournamentId` (`TournamentId`),
  KEY `ClubId` (`ClubId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournament_round`
--

DROP TABLE IF EXISTS `tournament_round`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournament_round` (
  `RoundId` int(11) NOT NULL AUTO_INCREMENT,
  `RoundName` varchar(20) NOT NULL,
  `TournamentId` int(11) unsigned NOT NULL,
  PRIMARY KEY (`RoundId`),
  KEY `TournamentId` (`TournamentId`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_group`
--

DROP TABLE IF EXISTS `user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_group` (
  `GroupId` int(11) NOT NULL AUTO_INCREMENT,
  `GroupName` varchar(30) NOT NULL,
  `Valid` int(1) DEFAULT 1,
  PRIMARY KEY (`GroupId`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `UserId` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(20) NOT NULL,
  `UserPassword` text NOT NULL,
  `GroupId` int(11) NOT NULL,
  PRIMARY KEY (`UserId`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-10 10:54:14
