CREATE DATABASE IF NOT EXISTS `xsl_searcher` DEFAULT character set utf8 COLLATE utf8_general_ci;

drop table if exists `hot_event`;

CREATE TABLE `hot_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `word` varchar(255) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

drop table if exists `hot_res`;

CREATE TABLE `hot_res` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `res_type` varchar(20) NOT NULL,
  `res_id` varchar(100) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=0 DEFAULT CHARSET=utf8 collate=utf8_general_ci;