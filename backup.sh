#!/bin/bash

# Directories
directory="minecraft-server"
backup_dir="/root/server_backup"
split_dir="server_backup/split_backups"

CHAT_ID="-1002420089111"

telegram_cli_path="/root/serverspace/telegram-cli"


# Clean the backup and split directories
clean_backup_dir() {
  echo "Cleaning files in $backup_dir..."
  rm -rf "$backup_dir"
  rm -rf "$split_dir"
  mkdir -p "$backup_dir" "$split_dir"
  echo "Backup directory cleaned."
}

# Create a tar backup
create_backup() {
  backup_file="${backup_dir}/server-backup.tar.gz"
  
  echo "Creating backup..."
  tar -czf "$backup_file" -C "$directory" --exclude="session.lock" .
  echo "$backup_file"
  
  # Split the backup file if it exceeds a particular size
  split -b 1024M "$backup_file" "$split_dir/backup.part_" 
}

upload_files() {

    if [[ ! -d "$split_dir" ]]; then
        echo "Error: Directory $split_dir does not exist."
        return 1
    fi

    if [[ ! -x "$telegram_cli_path" ]]; then
        echo "Error: Telegram CLI executable $telegram_cli_path not found or not executable."
        return 1
    fi

    for file in "$split_dir"/*; do
        if [[ -f "$file" ]]; then
            description=$(date +'%Y-%m-%d_%H-%M-%S')
            echo "Uploading file: $file with description: $description"
            "$telegram_cli_path" -g "$CHAT_ID" -F "$file" -d "$description"
            if [[ $? -ne 0 ]]; then
                echo "Error: Failed to upload file $file"
            else
                echo "Successfully uploaded $file"
            fi
        fi
    done
}

# Main process
clean_backup_dir
backup_file=$(create_backup)
upload_files

rm -rf "$backup_dir"
echo "All steps completed successfully."
