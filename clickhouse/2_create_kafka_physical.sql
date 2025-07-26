-- This is the physical table that will store the data consumed from the Kafka topic.
CREATE TABLE IF NOT EXISTS kafka_physical (
    event_type String,
    event_time DateTime64(3),
    symbol String,
    trade_id UInt64,
    price Float64,
    quantity Float64,
    trade_time DateTime64(3),
    is_market_maker UInt8,
    ignore UInt8
)
ENGINE = MergeTree -- This indicates that this is a physical table that will store the data.
PARTITION BY toDate(event_time)
ORDER BY (symbol, trade_time);
