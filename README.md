# minecraftserver-automation
My minecraft server automation process using telegram bot 
My Server Ip 👉️ ``` alex5402.me```
# Minecraft Server Telegram Bot

A Telegram bot designed to manage and monitor a Minecraft server. This bot allows administrators to start, stop, monitor, and manage backups for the server directly through Telegram commands. It is built using Python and integrates `pexpect` for server process management and `python-telegram-bot` for Telegram integration.

## Features

- **Start and Stop Server**: Start and stop the Minecraft server with commands.
- **Send Commands**: Execute Minecraft server commands directly through Telegram.
- **Server Monitoring**: Automatically checks if the server is running and restarts it if it crashes.
- **Clean Locks**: Remove lock files when needed.
- **Backup Management**: Trigger backups manually or schedule them.
- **Admin Management**: Restrict bot access to authorized users only.
- **Notification System**: Sends important notifications about server status and backups.

---

## Installation

### Prerequisites
1. **Python**: Ensure you have Python 3.8 or later installed.
2. **Telegram Bot Token**: Obtain a bot token from the [BotFather](https://core.telegram.org/bots#botfather).
3. **Dependencies**: Install required tools and libraries.
   ```bash
   sudo pacman -S screen curl   # For Arch Linux
   pip install python-telegram-bot pexpect apscheduler
   ```

### Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repository/minecraft-server-bot.git
   cd minecraft-server-bot
   ```

2. **Set Up Admins**:
   Create an `admins.json` file in the same directory:
   ```json
   {
       "admins": [123456789]
   }
   ```
   Replace `123456789` with the Telegram user ID of an admin.

3. **Configure Variables**:
   Edit the bot configuration variables in the script:
   - Replace `your_bot_token` with your Telegram bot token.
   - Set `MONITOR_CHAT_ID` to the Telegram group ID or chat ID where monitoring messages will be sent.

4. **Scripts**:
   Ensure the following scripts exist in the project directory:
   - `server.sh`: Script to start the Minecraft server.
   - `backup.sh`: Script to back up the server.
   - `clean.sh`: Script to clean up lock files.

5. **Run the Bot**:
   ```bash
   python bot.py
   ```

---

## Commands

### Admin Commands

| Command            | Description                             |
|--------------------|-----------------------------------------|
| `/start`           | Starts a conversation with the bot.     |
| `/startserver`     | Starts the Minecraft server.            |
| `/stop`            | Stops the Minecraft server.             |
| `/sendcommand <cmd>` | Sends a command to the server console. |
| `/clean`           | Cleans up server lock files.            |
| `/backup`          | Manually triggers a server backup.      |

### Monitoring
- The bot automatically monitors the server's status. If the server crashes, it attempts to restart and notifies the monitor chat.

---

## Configuration Details

### Files
- **`admins.json`**: Stores the list of admin user IDs.
- **`server.sh`**: Script to start the server.
- **`backup.sh`**: Script to create backups.
- **`clean.sh`**: Script to remove lock files.

### Variables
| Variable           | Description                                              |
|--------------------|----------------------------------------------------------|
| `ADMIN_FILE`       | Path to the admin configuration file.                    |
| `MONITOR_CHAT_ID`  | Telegram chat ID for monitoring notifications.           |
| `bot_token`        | Telegram bot token.                                      |
| `serverdelay`      | Minimum wait time before stopping the server (seconds).  |
| `backup_folder`    | Folder to store server backups.                          |
| `serveris_on`      | Tracks the server's running state.                       |

---

## Notifications
The bot sends notifications for:
- Server crashes and restarts.
- Backup start and completion.
- Errors encountered during script execution.

---

## Scheduler

The bot uses `apscheduler` to schedule daily backups at 3:00 AM. You can modify the schedule in the `main` function:
```python
scheduler.add_job(execute_backup_script, 'cron', hour=3, minute=0)
```

---

## Known Issues

1. Ensure `server.sh`, `backup.sh`, and `clean.sh` are executable and correctly configured.
   ```bash
   chmod +x server.sh backup.sh clean.sh
   ```

2. If the bot crashes unexpectedly, check for errors in your `admins.json` file or missing dependencies.

---

## License
This project is open-source and available under the MIT License. Feel free to contribute and customize.

---

## Author
Created by [@alex5402](https://t.me/alex5402).




