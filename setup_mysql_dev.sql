-- Prepares a MySQL server for the project (development environment)
-- Creates the database hbnb_dev_db and the user hbnb_dev (password hbnb_dev_pwd)
-- Re-running this script does not fail
CREATE DATABASE IF NOT EXISTS hbnb_dev_db;
-- Create the user only if it does not exist yet
CREATE USER IF NOT EXISTS 'hbnb_dev'@'localhost' IDENTIFIED BY 'hbnb_dev_pwd';
-- All privileges on hbnb_dev_db only
GRANT ALL PRIVILEGES ON `hbnb_dev_db`.* TO 'hbnb_dev'@'localhost';
-- SELECT privilege on performance_schema only
GRANT SELECT ON `performance_schema`.* TO 'hbnb_dev'@'localhost';
-- Apply the privileges
FLUSH PRIVILEGES;
