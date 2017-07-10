-- phpMyAdmin SQL Dump
-- version 4.2.7.1
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Nov 24, 2014 at 01:25 AM
-- Server version: 5.6.20
-- PHP Version: 5.5.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `robot`
--
CREATE DATABASE IF NOT EXISTS `robot` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `robot`;

DELIMITER $$
--
-- Functions
--
CREATE DEFINER=`root`@`localhost` FUNCTION `getFeedbackAnalysis`(face_filename TEXT) RETURNS text CHARSET utf8
    READS SQL DATA
BEGIN
  DECLARE result TEXT;
  DECLARE wrong_dist DECIMAL(10,8) DEFAULT 9.99;
  DECLARE right_dist DECIMAL(10,8) DEFAULT 0.00;
  declare tempI INT;

  -- Selecionando feedbacks (negativos e positivos) da imagem
  select count(*) into tempI from tbl_face_user_feedback where matchfile = face_filename and feedback = 1;
  if tempI > 0 then
	select max(distance) into right_dist from tbl_face_user_feedback where matchfile = face_filename and feedback = 1;
  end if;
  select count(*) into tempI from tbl_face_user_feedback where matchfile = face_filename and feedback = 0;
  if tempI > 0 then
	select min(distance) into wrong_dist from tbl_face_user_feedback where matchfile = face_filename and feedback = 0;
  end if;
  
  set result = concat('right_max=',right_dist, ':', 'wrong_min=', wrong_dist);
  
  RETURN result;
END$$

CREATE DEFINER=`root`@`localhost` FUNCTION `hello_world`() RETURNS text CHARSET utf8
BEGIN
  RETURN 'Hello World';
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_face_user_feedback`
--

CREATE TABLE IF NOT EXISTS `tbl_face_user_feedback` (
  `id_resource` bigint(20) NOT NULL,
  `matchfile` varchar(200) NOT NULL,
  `distance` decimal(10,8) NOT NULL,
  `feedback` bit(1) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_landmark_position`
--

CREATE TABLE IF NOT EXISTS `tbl_landmark_position` (
  `id` bigint(20) NOT NULL,
  `dtb_datetime` datetime NOT NULL,
  `id_landmark` int(11) NOT NULL,
  `x` decimal(10,2) NOT NULL,
  `y` decimal(10,2) NOT NULL,
  `z` decimal(10,2) NOT NULL,
  `marker_x` decimal(10,2) NOT NULL,
  `marker_y` decimal(10,2) NOT NULL,
  `size_x` int(6) NOT NULL DEFAULT '0',
  `size_y` int(6) NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_ltm`
--

CREATE TABLE IF NOT EXISTS `tbl_ltm` (
  `id_resource` bigint(20) NOT NULL,
  `resource_text` varchar(21000) NOT NULL,
  `id_source` varchar(32) NOT NULL,
  `insert_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `weight` int(11) NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_stm`
--

CREATE TABLE IF NOT EXISTS `tbl_stm` (
  `id_resource` bigint(20) NOT NULL,
  `resource_text` varchar(21000) NOT NULL,
  `id_source` varchar(32) NOT NULL,
  `insert_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `stm_weight` int(11) NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Triggers `tbl_stm`
--
DELIMITER //
CREATE TRIGGER `after_insert_tbl_stm` AFTER INSERT ON `tbl_stm`
 FOR EACH ROW BEGIN
		declare match_file varchar(200);
		declare dist float;
		declare feed_back INT;
		DECLARE tempV VARCHAR(200);
		declare tempI INT;
		
		-- getting values from xml
		-- resource type_text
		select LOCATE('face_user_feedback', NEW.resource_text) into tempI;
		if tempI > 0 then
			-- matchfile
			select substr(NEW.resource_text, (SELECT LOCATE('<matches>', NEW.resource_text)+9), 200) into tempV;
			select left(tempV, (SELECT LOCATE('</', tempV)-1)) into match_file;
			-- distance
			select substr(NEW.resource_text, (SELECT LOCATE('<dist>', NEW.resource_text)+6), 20) into tempV;
			select cast(left(tempV, (SELECT LOCATE('</', tempV)-1)) as decimal(10,8)) into dist;
			-- feedback
			select substr(NEW.resource_text, (SELECT LOCATE('<feedback>', NEW.resource_text)+10), 20) into tempV;
			select cast(left(tempV, (SELECT LOCATE('</', tempV)-1)) as unsigned) into feed_back;
			-- inserting new register
			INSERT INTO tbl_face_user_feedback (id_resource, matchfile, distance, feedback)
			VALUES (NEW.id_resource, match_file, dist, feed_back);
		end if;
    END
//
DELIMITER ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_face_user_feedback`
--
ALTER TABLE `tbl_face_user_feedback`
 ADD PRIMARY KEY (`id_resource`), ADD KEY `matchfile` (`matchfile`,`feedback`);

--
-- Indexes for table `tbl_ltm`
--
ALTER TABLE `tbl_ltm`
 ADD PRIMARY KEY (`id_resource`);

--
-- Indexes for table `tbl_stm`
--
ALTER TABLE `tbl_stm`
 ADD PRIMARY KEY (`id_resource`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
