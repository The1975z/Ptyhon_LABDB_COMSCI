# Python LAB DB

โปรเจ็กต์นี้เป็นระบบการจัดการตัวละครอนิเมะ ที่พัฒนาโดยใช้ Python และ Tkinter สำหรับการสร้าง GUI รวมถึงการเชื่อมต่อกับฐานข้อมูล MySQL โดยใช้ MySQL Connector ทํา CRUD
## COMSCI-LABDB

## วิธีการใช้งาน

1. คลิกที่แท็บ `Search` เพื่อค้นหาตัวละครในฐานข้อมูล
2. ใช้แท็บ `Insert` เพื่อเพิ่มตัวละครใหม่ลงในฐานข้อมูล
3. สามารถแก้ไขตัวละครได้ที่แท็บ `Update`
4. ใช้แท็บ `Delete` เพื่อลบตัวละครออกจากฐานข้อมูล
5. แท็บ `LABAPI` และ `LABAPIMOVIE` สามารถใช้เพื่อดึงข้อมูลจาก API ภายนอก
ปล LABAPI ดึงมาจาก 
https://opend.data.go.th/get-ckan/datastore_search?resource_id=
 LABAPIMOVIE ดึงมาจาก
https://online-movie-database.p.rapidapi.com/auto-complete

## การตั้งค่า

โปรเจ็กต์นี้ใช้ `.env` ในการจัดการกับข้อมูลการเชื่อมต่อฐานข้อมูล โปรดตั้งค่าตัวแปรดังนี้:

```bash
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=anime_db // ตั้งชื่อตาม ชื่อdb ตัวเอง 



## Command SQL

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- สร้างตาราง anime
CREATE TABLE `anime` (
  `id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `numOfVolume` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- เพิ่มข้อมูลในตาราง anime
INSERT INTO `anime` (`id`, `title`, `numOfVolume`) VALUES
(1, 'Naruto', 72),
(2, 'One Piece', 100),
(3, 'Dragon Ball', 42),
(4, 'karakai-jouzu-no-takagi-san', 17);

-- สร้างตาราง characters
CREATE TABLE `characters` (
  `id` int(11) NOT NULL,
  `fName` varchar(255) DEFAULT NULL,
  `lName` varchar(255) DEFAULT NULL,
  `popularity` int(11) DEFAULT NULL,
  `animeFK` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- เพิ่มข้อมูลในตาราง characters
INSERT INTO `characters` (`id`, `fName`, `lName`, `popularity`, `animeFK`) VALUES
(2, 'Monkey D.', 'Luffy', 95, 2),
(3, 'Son', 'Goku', 90, 3),
(512341, 'Waree', 'Waree', 1, 1),
(512342, 'TESTSUNA', 'TESTSUNA', 1, 1),
(550650, 'New', 'Character', 50, 1),
(550651, 'New', 'Character', 50, 1),
(550600509, 'Takagi', 'San', 100, 4);




-- สร้าง index และ primary key ในตาราง anime
ALTER TABLE `anime`
  ADD PRIMARY KEY (`id`);

-- สร้าง index และ primary key ในตาราง characters
ALTER TABLE `characters`
  ADD PRIMARY KEY (`id`),
  ADD KEY `animeFK` (`animeFK`);

-- ตั้งค่า AUTO_INCREMENT สำหรับตาราง anime
ALTER TABLE `anime`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

-- ตั้งค่า AUTO_INCREMENT สำหรับตาราง characters
ALTER TABLE `characters`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=550600510;

-- เพิ่ม constraint ให้กับตาราง characters
ALTER TABLE `characters`
  ADD CONSTRAINT `characters_ibfk_1` FOREIGN KEY (`animeFK`) REFERENCES `anime` (`id`) ON DELETE SET NULL;

COMMIT;

