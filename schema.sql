-- CivicSignal relational schema (MySQL 8+). Column/table names match app.py ORM models.
CREATE DATABASE IF NOT EXISTS civicsignal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE civicsignal;

CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('citizen','staff','admin') NOT NULL DEFAULT 'citizen',
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(80) NOT NULL UNIQUE,
  description VARCHAR(255)
);

CREATE TABLE complaints (
  id INT PRIMARY KEY AUTO_INCREMENT,
  tracking_code VARCHAR(24) NOT NULL UNIQUE,
  reporter_id INT NOT NULL,
  category_id INT NOT NULL,
  title VARCHAR(140) NOT NULL,
  description TEXT NOT NULL,
  location_text VARCHAR(255) NOT NULL,
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6),
  priority ENUM('low','medium','high') NOT NULL DEFAULT 'medium',
  status ENUM('submitted','acknowledged','assigned','in_progress','resolved','verified','reopened','rejected') NOT NULL DEFAULT 'submitted',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_complaints_reporter FOREIGN KEY (reporter_id) REFERENCES users(id),
  CONSTRAINT fk_complaints_category FOREIGN KEY (category_id) REFERENCES categories(id),
  CONSTRAINT chk_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
  CONSTRAINT chk_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
  INDEX idx_complaints_status (status),
  INDEX idx_complaints_reporter (reporter_id),
  INDEX idx_complaints_category (category_id),
  INDEX idx_complaints_status_created (status, created_at)
);

CREATE TABLE assignments (
  id INT PRIMARY KEY AUTO_INCREMENT,
  complaint_id INT NOT NULL,
  staff_id INT NOT NULL,
  assigned_by INT NOT NULL,
  assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  note VARCHAR(500),
  CONSTRAINT fk_assignments_complaint FOREIGN KEY (complaint_id) REFERENCES complaints(id),
  CONSTRAINT fk_assignments_staff FOREIGN KEY (staff_id) REFERENCES users(id),
  CONSTRAINT fk_assignments_assigner FOREIGN KEY (assigned_by) REFERENCES users(id),
  INDEX idx_assignments_staff (staff_id, complaint_id)
);

CREATE TABLE status_history (
  id INT PRIMARY KEY AUTO_INCREMENT,
  complaint_id INT NOT NULL,
  changed_by INT NOT NULL,
  old_status VARCHAR(30),
  new_status VARCHAR(30) NOT NULL,
  note VARCHAR(500),
  changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_history_complaint FOREIGN KEY (complaint_id) REFERENCES complaints(id),
  CONSTRAINT fk_history_actor FOREIGN KEY (changed_by) REFERENCES users(id),
  INDEX idx_history_complaint_time (complaint_id, changed_at)
);

CREATE TABLE evidence (
  id INT PRIMARY KEY AUTO_INCREMENT,
  complaint_id INT NOT NULL,
  uploaded_by INT NOT NULL,
  evidence_type ENUM('before','after','other') NOT NULL DEFAULT 'other',
  blob_url VARCHAR(700) NOT NULL,
  original_filename VARCHAR(255) NOT NULL,
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_evidence_complaint FOREIGN KEY (complaint_id) REFERENCES complaints(id),
  CONSTRAINT fk_evidence_uploader FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

CREATE TABLE verifications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  complaint_id INT NOT NULL,
  verified_by INT NOT NULL,
  result ENUM('confirmed_fixed','still_unresolved') NOT NULL,
  comment VARCHAR(1000),
  verified_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_verifications_complaint FOREIGN KEY (complaint_id) REFERENCES complaints(id),
  CONSTRAINT fk_verifications_user FOREIGN KEY (verified_by) REFERENCES users(id)
);

CREATE TABLE activity_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  actor_id INT NULL,
  action VARCHAR(100) NOT NULL,
  entity_type VARCHAR(60) NOT NULL,
  entity_id INT,
  ip_address VARCHAR(45),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_activity_actor FOREIGN KEY (actor_id) REFERENCES users(id)
);

CREATE OR REPLACE VIEW v_complaint_summary AS
SELECT c.id AS complaint_id, c.tracking_code, c.title, cat.name AS category_name,
       c.location_text, c.priority, c.status, u.full_name AS reporter_name, c.created_at
FROM complaints c
JOIN categories cat ON cat.id = c.category_id
JOIN users u ON u.id = c.reporter_id;

DELIMITER //
CREATE PROCEDURE sp_reopen_complaint(
  IN p_complaint_id INT, IN p_actor_id INT, IN p_reason VARCHAR(500)
)
BEGIN
  DECLARE v_old_status VARCHAR(30);
  START TRANSACTION;
  SELECT status INTO v_old_status FROM complaints
    WHERE id = p_complaint_id FOR UPDATE;
  IF v_old_status IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Complaint not found';
  END IF;
  UPDATE complaints SET status = 'reopened' WHERE id = p_complaint_id;
  INSERT INTO status_history(complaint_id, changed_by, old_status, new_status, note)
    VALUES(p_complaint_id, p_actor_id, v_old_status, 'reopened', p_reason);
  COMMIT;
END//
DELIMITER ;

INSERT INTO categories(name, description) VALUES
('Road and pothole','Damaged roads and potholes'),
('Waste management','Garbage and sanitation'),
('Water supply','Leaks and water supply issues'),
('Street lighting','Broken or missing streetlights'),
('Drainage','Blocked drains and waterlogging');
