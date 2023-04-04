set -e

mongosh <<EOF
db = db.getSiblingDB('$MONGO_INITDB_DATABASE')

db.createUser({
  user: '$MONGO_USER',
  pwd: '$MONGO_PASS',
  roles: [{ role: 'readWrite', db: '$MONGO_INITDB_DATABASE' }],
});
db.createCollection('topics')
db.createCollection('messages')

EOF