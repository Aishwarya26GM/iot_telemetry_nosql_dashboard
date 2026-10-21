# How to explain the project

## Architecture
Streamlit is the presentation layer; Python uses PyMongo to send commands to MongoDB. MongoDB stores flexible telemetry documents in `telemetry_events` and device metadata in `devices`.

## Pages
- **Overview:** summary metrics and charts generated from MongoDB queries.
- **Telemetry Explorer:** filters readings and performs insert/update/delete operations.
- **Aggregation Lab:** displays and runs server-side aggregation pipelines.
- **Performance & Sharding:** creates indexes, displays `explain()` execution stats, and checks if the connection is through `mongos`.

## Complex query example
The “Average temperature by building” pipeline:
1. `$match` selects documents that have temperature readings.
2. `$group` groups by `location.building`, calculating `$avg`, `$max`, and `$sum`.
3. `$sort` ranks buildings by average temperature.

The “Facet dashboard summary” uses `$facet` to run several summary pipelines in one command. Other examples demonstrate `$unwind`, `$dateTrunc`, `$objectToArray`, `$lookup`, `$cond`, `$addToSet`, and `$limit`.

## Indexes and explain()
Indexes help MongoDB locate matching documents without scanning all documents in some query plans. `explain()` reports the winning plan and execution statistics, including documents and index keys examined. An index is not guaranteed to make every query faster; results depend on selectivity, sort, and query shape.

## Sharding truth
The dashboard only checks whether the connection is through a `mongos` router. A standalone MongoDB server is not sharded. Actual sharding needs a configured sharded cluster (config servers, shard replica sets, mongos, and an appropriate shard key). Do not describe the local standalone database as sharded.
