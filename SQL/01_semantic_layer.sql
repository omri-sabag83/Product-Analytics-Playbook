-- Module 1: the semantic layer, queried directly.
--
-- How to run (VS Code, SQLite extension by alexcvzz):
--   1. Cmd+Shift+P -> "SQLite: Use Database" -> pick data/processed/playbook.sqlite (once per session)
--   2. Put the cursor in a query, right-click -> "Run Selected Query" (or "Run Query" for the whole file)
--
-- Tables:
--   events             raw sampled log, uncleaned (2,026,833 rows)
--   events_clean       duplicates dropped, negative prices set aside
--   refund_candidates  the 14 negative-price purchase rows
--   orders             one row per inferred order (user + session + second): lines, revenue
--   daily_active       one row per user per active day
--
-- The file is built by data/get_data.py (or common.build_sqlite()); rebuild it after editing views.sql.


-- Orders and revenue by month
SELECT event_month,
       COUNT(*)                                  AS orders,
       ROUND(SUM(revenue), 2)                    AS revenue,
       ROUND(SUM(revenue) * 1.0 / COUNT(*), 2)   AS avg_order_value
FROM orders
GROUP BY event_month;


-- Raw vs. clean event counts
SELECT r.event_type, r.raw, c.clean, r.raw - c.clean AS removed
FROM (SELECT event_type, COUNT(*) AS raw   FROM events       GROUP BY 1) r
JOIN (SELECT event_type, COUNT(*) AS clean FROM events_clean GROUP BY 1) c USING (event_type)
ORDER BY removed DESC;


-- The 10 biggest orders
SELECT user_id, event_time, lines, ROUND(revenue, 2) AS revenue
FROM orders
ORDER BY lines DESC
LIMIT 10;


-- Daily active users, average per month
SELECT event_month, ROUND(AVG(users), 1) AS avg_daily_active_users
FROM (SELECT event_month, event_date, COUNT(*) AS users FROM daily_active GROUP BY 1, 2)
GROUP BY event_month;
