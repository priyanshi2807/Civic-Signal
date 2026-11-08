USE civicsignal;

-- 1. INNER JOIN: complaints with their reporters and categories
SELECT c.tracking_code, c.title, u.full_name, cat.name AS category_name, c.status
FROM complaints c
INNER JOIN users u ON u.id = c.reporter_id
INNER JOIN categories cat ON cat.id = c.category_id;

-- 2. LEFT JOIN: include categories with no complaints
SELECT cat.name AS category_name, COUNT(c.id) AS complaint_count
FROM categories cat
LEFT JOIN complaints c ON c.category_id = cat.id
GROUP BY cat.id, cat.name;

-- 3. GROUP BY / HAVING: categories with at least two complaints
SELECT category_id, COUNT(*) AS total
FROM complaints
GROUP BY category_id
HAVING COUNT(*) >= 2;

-- 4. View
SELECT * FROM v_complaint_summary ORDER BY created_at DESC;

-- 5. Transaction demonstration (use valid IDs in a test database)
START TRANSACTION;
UPDATE complaints SET priority = 'high' WHERE id = 1;
-- Inspect the change, then choose exactly one:
COMMIT;
-- ROLLBACK; -- use instead of COMMIT to undo the test update

-- 6. Index-friendly search
SELECT id, tracking_code, status, created_at
FROM complaints
WHERE status = 'submitted'
ORDER BY created_at DESC;

-- 7. Analytics: status distribution
SELECT status, COUNT(*) AS total
FROM complaints
GROUP BY status;
