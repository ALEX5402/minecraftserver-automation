#!/bin/bash
# Path to your Minecraft server jar file
SERVER_JAR="server.jar"

# Minimum amount of memory to allocate
MIN_MEMORY="2G"

# Maximum amount of memory to allocate
MAX_MEMORY="10G"
CURRENT_DIR="$(pwd)"
echo $CURRENT_DIR

# Function to start the server
cd "server"
echo "eula=true" > eula.txt
java -Xms$MIN_MEMORY -Xmx$MAX_MEMORY -jar $SERVER_JAR nogui


#screen -S minectaftserver -d -m java -Xms$MIN_MEMORY -Xmx$MAX_MEMORY -jar $SERVER_JAR nogui
#screen -r minectaftserver
