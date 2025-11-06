-- MySQL dump 10.13  Distrib 8.0.37, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: tienda_db
-- ------------------------------------------------------
-- Server version	8.0.37

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cart_items`
--

DROP TABLE IF EXISTS `cart_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `product_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `product_id` (`product_id`),
  KEY `ix_cart_items_id` (`id`),
  CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cart_items`
--

LOCK TABLES `cart_items` WRITE;
/*!40000 ALTER TABLE `cart_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `cart_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text,
  `precio` float NOT NULL,
  `stock` int DEFAULT NULL,
  `imagen_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_products_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'Camisa de Lino Blanca','Camisa fresca de lino, ideal para verano.',45.99,39,'https://tse4.mm.bing.net/th/id/OIP.r7yu4kWSRmm6PCecz7h7MwHaLG?rs=1&pid=ImgDetMain&o=7&rm=3'),(2,'Pantalón Vaquero Clásico','Pantalón vaquero (jean) de corte recto.',70,22,'https://m.media-amazon.com/images/I/71caydI6MYL._AC_SL1500_.jpg'),(3,'Tenis Skechers','Cómodas para correr o caminar.',89.5,71,'https://tse4.mm.bing.net/th/id/OIP.jxyYLK45BKWIL6HKPj5SVwHaGj?rs=1&pid=ImgDetMain&o=7&rm=3'),(4,'Camisa Polo','Camisa Polo de Calidad',200,6,'https://i5.walmartimages.com.mx/samsmx/images/product-images/img_large/981010395l.jpg?odnHeight=612&odnWidth=612&odnBg=FFFFFF'),(5,'Pantalón Furor','Pantalón Furor para Hombre, de Gabardina Khaki Talla 34',250,4,'https://i5.walmartimages.com.mx/mg/gm/3pp/asr/44325502-7047-48cd-8724-8a3254b43d2c.55385f68622a7e9c8fb2f784525d9162.jpeg?odnHeight=612&odnWidth=612&odnBg=FFFFFF'),(6,'nike tenis','confort pa tus pies',200,0,'https://tse4.mm.bing.net/th/id/OIP.WLbsWsMjC6TVNyDqdQDnIQHaF7?rs=1&pid=ImgDetMain&o=7&rm=3');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) DEFAULT NULL,
  `nombre_completo` varchar(255) DEFAULT NULL,
  `hashed_password` varchar(255) DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `direccion` text,
  `ciudad` varchar(100) DEFAULT NULL,
  `estado` varchar(100) DEFAULT NULL,
  `codigo_postal` varchar(20) DEFAULT NULL,
  `pais` varchar(100) DEFAULT NULL,
  `telefono` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'mario@gmail.com','Mario Guierres Hernandez','$2b$12$7R484nV6FfZ7BUUJYY5nheYU5Zz0zIyNf9V65KR4q0iVF/BCpDeXO',0,'Lazaro Cardenas 40','Jiquilpan','Michoacan','53123','Mexico','3531265067'),(2,'admin@gmail.com','Admin','$2b$12$tqMrW/NQ6DcJjdnRGMoipOwFrMvV1hOklFV6x4A3gK8XVcTcFK.KG',1,'av independencia 35#','Guadalajara','Jalisco','24432','Mexico','3531245433'),(3,'rodrigo@gmail.com','Rodrigo Marnites','$2b$12$AcC/8u9mMM2ElyzQwNWueejG2zWdeDQbyxbCIeoIs4OFe1c1timJy',0,'8 de mayo','Zapopan','Jalisco','21332','Mexico','3512331253'),(4,'jose@gmail.com','Jose arturo maduro','$2b$12$.L1zG5fBEb6F9VC6SAh2OuxCZ.VXTgDwb0S.xdFei9roNrpRMP8ey',0,'Mendranos','Jiquilpan','Michoacan','59510','Mexico','3531265060');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `venta_items`
--

DROP TABLE IF EXISTS `venta_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `venta_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cantidad` int NOT NULL,
  `precio_unitario` float NOT NULL,
  `venta_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `venta_id` (`venta_id`),
  KEY `product_id` (`product_id`),
  KEY `ix_venta_items_id` (`id`),
  CONSTRAINT `venta_items_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`),
  CONSTRAINT `venta_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `venta_items`
--

LOCK TABLES `venta_items` WRITE;
/*!40000 ALTER TABLE `venta_items` DISABLE KEYS */;
INSERT INTO `venta_items` VALUES (1,1,45.99,1,1),(2,1,70,1,2),(3,1,89.5,2,3),(4,8,45.99,3,1),(5,2,70,3,2),(6,1,89.5,3,3),(7,2,200,3,4),(8,1,45.99,4,1),(9,1,70,4,2),(10,2,89.5,4,3),(11,2,70,5,2),(12,1,89.5,5,3),(13,2,200,5,4),(14,1,250,6,5),(15,2,45.99,7,1),(16,3,70,7,2);
/*!40000 ALTER TABLE `venta_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime DEFAULT NULL,
  `total` float NOT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_ventas_id` (`id`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,'2025-10-27 10:30:00',115.99,1),(2,'2025-10-28 14:15:00',89.5,1),(3,'2025-11-02 13:39:57',997.42,3),(4,'2025-11-02 15:36:03',294.99,4),(5,'2025-11-02 18:20:58',629.5,1),(6,'2025-11-02 18:24:49',250,1),(7,'2025-11-03 13:32:24',301.98,1);
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-05 16:48:26
