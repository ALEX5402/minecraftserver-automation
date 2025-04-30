#!/bin/bash

SERVER_DIR="./server"
BACKUP_DIR="./temp/server_backup"
SPLIT_DIR="$BACKUP_DIR/split_backups"

CHAT_ID="-1002420089111"
TELEGRAM_CLI="./telegram-cli"

clean_backup_dir() {
  echo "🔄 Cleaning backup directories..."
  rm -rf "$BACKUP_DIR"
  mkdir -p "$SPLIT_DIR"
  echo "✅ Directories cleaned."
}

create_backup() {
  local backup_file="${BACKUP_DIR}/server-backup-$(date '+%Y-%m-%d_%H-%M-%S').tar.gz"

  echo "🔄 Creating backup..."
  tar -czf "$backup_file" -C "$SERVER_DIR" --exclude="session.lock" .
  echo "✅ Backup created: $backup_file"
  split -b 1500M "$backup_file" "$SPLIT_DIR/backup.part_"
}

upload_files() {
  if [[ ! -x "$TELEGRAM_CLI" ]]; then
    echo "❌ Error: telegram-cli not found or not executable at $TELEGRAM_CLI"
    exit 1
  fi

  echo "🔄 Uploading backup files to Telegram..."

  for file in "$SPLIT_DIR"/*; do
    if [[ -f "$file" ]]; then
      local description="Backup part uploaded at $(date '+%Y-%m-%d %H:%M:%S')"
      echo "🔼 Uploading: $file"
      "$TELEGRAM_CLI" -g "$CHAT_ID" -F "$file" -d "$description"

      if [[ $? -ne 0 ]]; then
        echo "❌ Error uploading $file"
      else
        echo "✅ Successfully uploaded $file"
      fi
    fi
  done
}


send_final_message() {
  local date_now=$(date '+%Y-%m-%d %H:%M:%S')
  "$TELEGRAM_CLI" -g "$CHAT_ID" -t "✅ Backup completed successfully at: $date_now"
  echo "📢 Final notification sent."
}


clean_backup_dir
create_backup
upload_files
send_final_message

rm -rf "$BACKUP_DIR"
echo "🧹 Backup files cleaned up."

echo "🎉 Backup process completed successfully."