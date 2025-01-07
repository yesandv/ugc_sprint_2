#!/bin/sh

wait_for_mongo() {
  host=$1
  port=$2

  echo "Waiting for an instance at ${host}:${port} to be ready"
  while ! mongosh --host "${host}" --port "${port}" --eval "db.runCommand({ ping: 1 })" >/dev/null 2>&1; do
    echo "Instance at ${host}:${port} is not ready. Retrying in 2 seconds"
    sleep 2
  done
  echo "Instance at ${host}:${port} is ready"
}

MONGO_HOSTS="mongocfg1 mongocfg2 mongocfg3 mongors1n1 mongors2n1"

for host in $MONGO_HOSTS; do
  wait_for_mongo "$host" "$MONGO_PORT"
done

echo "Initializing config server replica set"
mongosh --host "mongocfg1" --port "${MONGO_PORT}" --eval "
rs.initiate({
  _id: \"mongors1conf\",
  configsvr: true,
  members: [
    { _id: 0, host: \"mongocfg1:${MONGO_PORT}\" },
    { _id: 1, host: \"mongocfg2:${MONGO_PORT}\" },
    { _id: 2, host: \"mongocfg3:${MONGO_PORT}\" }
  ]
})
"

echo "Initializing shard replica set 1"
mongosh --host "mongors1n1" --port "${MONGO_PORT}" --eval "
rs.initiate({
  _id: \"mongors1\",
  members: [
    { _id: 0, host: \"mongors1n1:${MONGO_PORT}\" },
    { _id: 1, host: \"mongors1n2:${MONGO_PORT}\" },
    { _id: 2, host: \"mongors1n3:${MONGO_PORT}\" }
  ]
})
"

echo "Adding shard 1 to the cluster"
mongosh --host "mongos1" --port "${MONGO_PORT}" --eval "
sh.addShard(\"mongors1/mongors1n1:${MONGO_PORT}\")
"

echo "Initializing shard replica set 2"
mongosh --host "mongors2n1" --port "${MONGO_PORT}" --eval "
rs.initiate({
  _id: \"mongors2\",
  members: [
    { _id: 0, host: \"mongors2n1:${MONGO_PORT}\" },
    { _id: 1, host: \"mongors2n2:${MONGO_PORT}\" },
    { _id: 2, host: \"mongors2n3:${MONGO_PORT}\" }
  ]
})
"

echo "Adding shard 2 to the cluster"
mongosh --host "mongos2" --port "${MONGO_PORT}" --eval "
sh.addShard(\"mongors2/mongors2n1:${MONGO_PORT}\")
"

echo "Use the database"
mongosh --host "mongors1n1" --port "${MONGO_PORT}" --eval "
use $MONGO_DB
"

echo "Enabling sharding"
mongosh --host "mongos1" --port "${MONGO_PORT}" --eval "
sh.enableSharding(\"$MONGO_DB\")
"

echo "Creating collections"
mongosh --host "mongos1" --port "${MONGO_PORT}" --eval "
const db = db.getSiblingDB(\"${MONGO_DB}\");
db.createCollection(\"${BOOKMARK_COLLECTION}\");
db.createCollection(\"${LIKE_COLLECTION}\");
db.createCollection(\"${REVIEW_COLLECTION}\");
"

echo "Sharding collections"
mongosh --host "mongos1" --port "${MONGO_PORT}" --eval "
sh.shardCollection(\"${MONGO_DB}.${BOOKMARK_COLLECTION}\", {\"id\": \"hashed\"});
sh.shardCollection(\"${MONGO_DB}.${LIKE_COLLECTION}\", {\"id\": \"hashed\"});
sh.shardCollection(\"${MONGO_DB}.${REVIEW_COLLECTION}\", {\"id\": \"hashed\"});
"

echo "MongoDB cluster setup is complete"
