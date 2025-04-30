# Minecraft Bot Automation

This project provides a secure and easy-to-use Minecraft server control panel integrated into a Telegram bot. It allows authorized users to manage and interact with a Minecraft server through Telegram commands, perform secure backups, and access a live web-based terminal.

## have a look
![Screenshot_20250430_115640](https://github.com/user-attachments/assets/bba5cb9f-952c-4b87-87d9-f41f684ece27)

## Features

- **Server Control**: Start and stop the Minecraft server directly from Telegram.
- **Live Web Terminal**: Access a real-time web-based terminal protected by a dynamically generated password.
- **Secure Access**: Terminal sessions are secured with strong, randomly generated passwords provided via Telegram.
- **Backup System**: Create server backups via Telegram with automated splitting and uploading to Telegram using [telegram-cli](https://github.com/ALEX5402/telegram-cli).
- **Authorization**: Restrict bot commands to specific authorized Telegram user IDs.
- **Responsive Web Interface**: The web terminal interface is optimized for performance by limiting logs to prevent browser lag.

## Setup

### Prerequisites

- Node.js (>= 16.x)
- npm
- Telegram Bot Token (from @BotFather)
- [telegram-cli](https://github.com/ALEX5402/telegram-cli/releases/tag/1.0.0-beta) for backup uploads
- Minecraft Server files located in the `./server` directory

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env` file in the project root with the following content:

```env
BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_IDS=telegram_user_id1,telegram_user_id2
SERVER_PORT=your_desired_port
```

4. Make scripts executable:

```bash
chmod +x start.sh backup.sh telegram-cli
```

### Usage

- **Start the bot server**:

```bash
node server.js
```

## Telegram Commands

- `/startserver`: Start the Minecraft server.
- `/stopserver`: Stop the Minecraft server.
- `/terminal`: Generate a secure password and get a link to access the live web-based terminal.
- `/backup`: Perform a secure backup of the server and upload it to Telegram.

## Web Terminal

- Access URL: Provided dynamically via the Telegram bot when issuing the `/terminal` command.
- Authentication: A randomly generated password sent as a spoiler-formatted Telegram message.

## Directory Structure

```bash
├── server.js          # Main bot server file
├── backup.sh          # Backup script
├── start.sh           # Script to start Minecraft server
├── telegram-cli       # CLI to upload backup files to Telegram
├── server             # Directory containing Minecraft server files
├── public             # Directory containing the web interface
│   └── terminal.html  # Terminal interface
├── .env               # Configuration file
├── package.json
└── package-lock.json
```

## Security

- Passwords are securely generated with strong randomization (40 characters with symbols).
- Terminal sessions expire once the bot session is invalidated.

## License

MIT License

---

Enjoy managing your Minecraft server securely and conveniently!
