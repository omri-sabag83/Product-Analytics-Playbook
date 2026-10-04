-- Peek at each semantic-layer table: 5 rows each, plus its row count.
--
-- How to run (VS Code, SQLite extension by alexcvzz):
--   1. Cmd+Shift+P -> "SQLite: Use Database" -> pick data/processed/playbook.sqlite (once per session)
--   2. Put the cursor in a query, right-click -> "Run Selected Query"


-- events_clean: all events after Rules 1-3 (Module 1, Part 3)
SELECT * FROM events_clean LIMIT 5;

-- refund_candidates: the negative-price purchase rows
SELECT * FROM refund_candidates LIMIT 5;

-- orders: one row per rebuilt order (user + session + second)
SELECT * FROM orders LIMIT 5;

-- daily_active: one row per user per active day
SELECT * FROM daily_active LIMIT 5;


-- Row count of every table
SELECT 'events'            AS table_name, COUNT(*) AS rows FROM events
UNION ALL SELECT 'events_clean',      COUNT(*) FROM events_clean
UNION ALL SELECT 'refund_candidates', COUNT(*) FROM refund_candidates
UNION ALL SELECT 'orders',            COUNT(*) FROM orders
UNION ALL SELECT 'daily_active',      COUNT(*) FROM daily_active;
