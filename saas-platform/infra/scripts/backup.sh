#!/bin/bash
# Backup script for MySQL and Redis

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

echo "Backing up Master Database..."
docker exec mysql_container mysqldump -u root -p"$DB_PASSWORD" master_db > "$BACKUP_DIR/master.sql"

echo "Backing up Tenant Databases..."
# Logic to list and backup all tenant databases
databases=$(docker exec mysql_container mysql -u root -p"$DB_PASSWORD" -e "SHOW DATABASES LIKE 'tenant_%';" -s --skip-column-names)
for db in $databases; do
    docker exec mysql_container mysqldump -u root -p"$DB_PASSWORD" "$db" > "$BACKUP_DIR/$db.sql"
done

echo "Backing up Redis..."
docker exec redis_container redis-cli save
docker cp redis_container:/data/dump.rdb "$BACKUP_DIR/redis.rdb"

echo "Backup completed: $BACKUP_DIR"
