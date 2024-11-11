#!/bin/bash

echo "Starting backup script at $(date)"

if [ "$BACKUPS_ENABLED" != "1" ]; then
  echo "Backups are not enabled. Exiting."
  exit 0
fi

until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" -h "localhost"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

BACKUP_DIR="/backups/$APP_NAME"

SALT=$(date +%F_%H-%M-%S)_$(od -vN "8" -An -tx4 /dev/urandom | tr -d ' ')
FILENAME="backup_$SALT.dump"
ENCRYPTED_FILENAME="backup_$SALT.dump.gpg"


mkdir -p "$BACKUP_DIR"

pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -F c -f "$BACKUP_DIR/$FILENAME"

gpg --batch --yes --passphrase "$ENCRYPTION_PASSPHRASE" -c "$BACKUP_DIR/$FILENAME"

rm "$BACKUP_DIR/$FILENAME"

echo "Encrypted backup created at $BACKUP_DIR/$ENCRYPTED_FILENAME"

S3_PATH="s3://$AWS_STORAGE_BUCKET_NAME$BACKUP_DIR/$POSTGRES_HOST/$ENCRYPTED_FILENAME"

aws s3 cp "$BACKUP_DIR/$ENCRYPTED_FILENAME" "$S3_PATH" --endpoint-url "$AWS_S3_ENDPOINT_URL"

if [ $? -eq 0 ]; then
  echo "Backup successfully uploaded to S3: $S3_PATH"
else
  echo "Backup upload to S3 failed!"
fi
