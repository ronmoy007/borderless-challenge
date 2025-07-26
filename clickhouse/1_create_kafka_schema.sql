-- This "table" just defines the schema for the Kafka topic. In reality, it does not create a physical table in ClickHouse. Interesting.
CREATE TABLE IF NOT EXISTS kafka_schema (
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
ENGINE = Kafka -- This is the trick to indicate that is not a physical table but a schema for the Kafka topic.
SETTINGS
    kafka_broker_list = 'redpanda:9092',
    kafka_topic_list = 'borderless_challenge',
    kafka_group_name = 'clickhouse_consumer_group',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1;
