-- Prepares a MySQL server for the project (test environment)
-- Creates the database hbnb_test_db and the user hbnb_test (password hbnb_test_pwd)
-- Re-running this script does not fail
CREATE DATABASE IF NOT EXISTS hbnb_test_db;
-- Create the user only if it does not exist yet
CREATE USER IF NOT EXISTS 'hbnb_test'@'localhost' IDENTIFIED BY 'hbnb_test_pwd';
-- All privileges on hbnb_test_db only
GRANT ALL PRIVILEGES ON `hbnb_test_db`.* TO 'hbnb_test'@'localhost';
-- SELECT privilege on performance_schema only
GRANT SELECT ON `performance_schema`.* TO 'hbnb_test'@'localhost';
-- Apply the privileges
FLUSH PRIVILEGES;
