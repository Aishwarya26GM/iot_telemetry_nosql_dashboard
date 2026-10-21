# Optional real MongoDB sharding lab (local Docker)

This project runs normally against a standalone MongoDB server. For real sharding, use a local cluster and connect through `mongos`. Do not claim sharding when connected to a standalone server.

## Important
A correct MongoDB sharded cluster needs config servers, shard replica sets, and `mongos`. The complete deployment depends on the MongoDB version and Docker availability. Use MongoDB's official documentation for the current Docker/replica-set initialization syntax. Do not expose these lab ports to an untrusted network.

## Lab architecture
- Config server replica set: stores cluster metadata.
- Shard 1 replica set: holds a portion of sharded data.
- Shard 2 replica set: holds another portion.
- `mongos`: router used by the application.

## Enable sharding (run in mongosh connected to mongos)
After initializing config-server and shard replica sets and adding both shards to mongos, run:
```javascript
sh.addShard("shard1/SHARD1_HOST:27018")
sh.addShard("shard2/SHARD2_HOST:27019")
sh.enableSharding("iot_telemetry_lab")
```
Replace the hostnames/ports with the actual replica-set addresses from your cluster configuration.

For this dataset, a possible shard key is a compound key such as:
```javascript
sh.shardCollection("iot_telemetry_lab.telemetry_events", { tenant_id: 1, event_id: 1 })
```
Confirm that the shard key and existing indexes satisfy the rules of your installed MongoDB version. A unique index on `event_id` alone may not be compatible with this shard key. In a fresh sharded database, create compatible indexes and seed data after enabling sharding.

## Verify
```javascript
sh.status()
db.telemetry_events.getShardVersion()
```
Also connect to the router and run:
```javascript
db.adminCommand({ hello: 1 })
```
The response should include `msg: "isdbgrid"` when connected through mongos.

## Compare queries
Use the same query and indexes on an unsharded collection and a sharded collection. Run explain and compare actual execution statistics. Small local datasets may be slower when sharded due to routing overhead. Do not invent performance results.

This guide intentionally avoids shipping an unverified one-size-fits-all Docker Compose file: replica-set addresses and initialization must match the Docker network and MongoDB version used on your machine.
