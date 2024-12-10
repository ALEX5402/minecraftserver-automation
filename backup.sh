#!/bin/bash

# Directories change these based on your needs
directory="minecraft-server"
backup_dir="server_backup"
split_dir="server_backup/split_backups"

# Telegram bot token and chat ID
BOT_TOKEN="your_bot_token"
CHAT_ID="-1002420089111"

# GitHub repository details
GITHUB_OWNER="alex5402"
GITHUB_REPO="minecraftserver-automation"

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
  split -b 1840M "$backup_file" "$split_dir/backup.part_"
}

# Send GitHub release download link to Telegram
send_github_links() {
  release_tag="$(date +'%Y-%m-%d_%H-%M-%S')"
  release_title="$release_tag"

  echo "Creating a new GitHub release: $release_title"
  gh release create "$release_tag" "$split_dir"/* --repo "$GITHUB_OWNER/$GITHUB_REPO" --title "$release_title" --notes "Automated backup release"

  echo "Files uploaded to GitHub release: $release_title"
  download_url="https://github.com/$GITHUB_OWNER/$GITHUB_REPO/releases/tag/$release_tag"

  echo "Sending download link to Telegram..."
  curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
       -d chat_id="$CHAT_ID" \
       -d text="Backup completed! Download the files here: $download_url"
  echo "Download link sent to Telegram."
}

# Main process
clean_backup_dir
backup_file=$(create_backup)

# Upload split files to GitHub release and send link to Telegram
send_github_links

echo "All steps completed successfully."
