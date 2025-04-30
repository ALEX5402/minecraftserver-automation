require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const pty = require('node-pty');
const crypto = require('crypto');
const { exec } = require('child_process');

const authorizedIds = process.env.AUTHORIZED_IDS.split(',').map(id => id.trim());

const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static('public'));

let minecraftProcess = null;
let minecraftPTY = null;

let currentSession = null;
let currentPassword = null;
let sessionOutput = '';
let backupRunning = false;

const isServerRunning = () => minecraftProcess && !minecraftProcess.killed;

const generatePassword = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()-_=+[]{}|;:,.<>?';
  return Array.from(crypto.randomFillSync(new Uint32Array(40)))
    .map(x => chars[x % chars.length])
    .join('');
};

const isAuthorized = (chatId) => authorizedIds.includes(chatId.toString());

bot.onText(/\/startserver/, (msg) => {
  const chatId = msg.chat.id;
  if (!isAuthorized(chatId)) return;

  if (isServerRunning()) {
    bot.sendMessage(chatId, "⚠️ Server is already running.");
    return;
  }

  minecraftPTY = pty.spawn('bash', ['./start.sh'], {
    name: 'xterm-color',
    cols: 80,
    rows: 24,
    cwd: __dirname ,
    env: process.env
  });

  minecraftProcess = minecraftPTY;

  minecraftPTY.on('exit', () => {
    minecraftProcess = null;
  });

  bot.sendMessage(chatId, "✅ Minecraft server started successfully.");
});

bot.onText(/\/stopserver/, (msg) => {
  const chatId = msg.chat.id;
  if (!isAuthorized(chatId)) return;

  if (!isServerRunning()) {
    bot.sendMessage(chatId, "⚠️ Server is not currently running.");
    return;
  }

  minecraftPTY.write('stop\n');
  bot.sendMessage(chatId, "🛑 Server is stopping...");
});

bot.onText(/\/terminal/, (msg) => {
  const chatId = msg.chat.id;
  if (!isAuthorized(chatId)) return;

  if (!isServerRunning()) {
    bot.sendMessage(chatId, "⚠️ Server isn't running. Use /startserver first.");
    return;
  }

  currentPassword = generatePassword();
  currentSession = { active: true };
  sessionOutput = '';

  const url = `http://0.0.0.0:${process.env.SERVER_PORT}/terminal`;

  bot.sendMessage(chatId, `🖥️ Terminal URL: [Open Terminal](${url})\n🔑 Password: ||\`${currentPassword}\`||`, {
    parse_mode: 'MarkdownV2'
  });
});

bot.onText(/\/backup/, (msg) => {
  const chatId = msg.chat.id;
  if (!isAuthorized(chatId)) return;

  if (backupRunning) {
    bot.sendMessage(chatId, "⚠️ Backup already running. Please wait until it finishes.");
    return;
  }

  backupRunning = true;
  bot.sendMessage(chatId, "⏳ Backup started...");

  exec('bash ./backup.sh', { cwd: __dirname }, (error, stdout, stderr) => {
    backupRunning = false;

    if (error) {
      bot.sendMessage(chatId, `❌ Backup failed: ${stderr || error.message}`);
      return;
    }

    bot.sendMessage(chatId, "✅ Backup completed successfully.");
  });
});

bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  const text = msg.text;

  if (!isAuthorized(chatId)) return;

  if (!text.match(/^\/(startserver|stopserver|terminal|backup)$/)) {
    bot.sendMessage(chatId, "❌ Unknown command. Please use /startserver, /stopserver, /terminal, or /backup.");
  }
});

app.get('/terminal', (req, res) => {
  if (!currentSession || !currentSession.active) {
    return res.status(403).send('Session expired or invalid.');
  }
  res.sendFile(__dirname + '/public/terminal.html');
});

io.on('connection', (socket) => {
  socket.on('authenticate', (password) => {
    if (password !== currentPassword || !currentSession) {
      socket.emit('auth_failed');
      socket.disconnect();
      return;
    }

    socket.emit('authenticated');
    socket.emit('output', sessionOutput);

    const sendData = data => {
      sessionOutput += data;
      socket.emit('output', data);
    };

    minecraftPTY.on('data', sendData);

    socket.on('input', input => minecraftPTY.write(input));

    socket.on('disconnect', () => {
      minecraftPTY.removeListener('data', sendData);
    });
  });
});

server.listen(process.env.SERVER_PORT, () => {
  console.log(`Server running on port ${process.env.SERVER_PORT}`);
});
