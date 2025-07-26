-- This is the materialized view that will automatically insert data into the kafka_physical table from the kafka_schema topic. Super weird, I haven't seen this before.
CREATE MATERIALIZED VIEW IF NOT EXISTS kafka_materialized_view
TO kafka_physical
AS
SELECT *
FROM kafka_schema;
