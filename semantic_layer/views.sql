-- Semantic layer views (Module 1). Built on the raw table `events`.
-- Every later module reads these views, never `events` directly.

-- Rule 1: remove duplicates (rows identical in every column; cause unknown, see Module 1).
-- Rule 2: set aside negative-price rows. All of them are purchases; they may be
--         refunds (the log can't confirm it), so they live in refund_candidates
--         and feed net revenue only.
-- Nothing else is removed: zero prices and missing brands stay, and are flagged where they matter.
DROP VIEW IF EXISTS events_clean;
CREATE VIEW events_clean AS
SELECT DISTINCT event_time, event_type, product_id, category_id, category_code,
       brand, price, user_id, user_session,
       substr(event_time, 1, 10) AS event_date,
       substr(event_time, 1, 7)  AS event_month
FROM events
WHERE price >= 0;

DROP VIEW IF EXISTS refund_candidates;
CREATE VIEW refund_candidates AS
SELECT DISTINCT event_time, event_type, product_id, price, user_id, user_session,
       substr(event_time, 1, 10) AS event_date,
       substr(event_time, 1, 7)  AS event_month
FROM events
WHERE price < 0;

-- An order = all purchase lines with the same user, session and timestamp
-- (the log has no order id; Module 1 shows separate same-second groups in a session are
-- mostly separate checkouts, and none is split across sessions).
DROP VIEW IF EXISTS orders;
CREATE VIEW orders AS
SELECT user_id, user_session, event_time,
       event_date, event_month,
       COUNT(*)   AS lines,
       SUM(price) AS revenue
FROM events_clean
WHERE event_type = 'purchase'
GROUP BY user_id, user_session, event_time;

-- One row per user per day with any clean event.
DROP VIEW IF EXISTS daily_active;
CREATE VIEW daily_active AS
SELECT user_id, event_date, event_month,
       COUNT(*) AS events,
       MAX(event_type = 'purchase') AS purchased
FROM events_clean
GROUP BY user_id, event_date;
