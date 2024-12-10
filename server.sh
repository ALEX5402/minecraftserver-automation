#!/bin/bash
# Path to your Minecraft server jar file
SERVER_JAR="server.jar"

# Minimum amount of memory to allocate
MIN_MEMORY="1G"

# Maximum amount of memory to allocate
MAX_MEMORY="2G"

# Function to start the server
cd minecraft-server
screen -S minectaftserver -d -m java -Xms$MIN_MEMORY -Xmx$MAX_MEMORY -jar $SERVER_JAR nogui
screen -r minectaftserver
