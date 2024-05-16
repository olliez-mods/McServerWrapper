# Minecraft Server Wrapper

This script allows you to get chat, send chat, and send commands to a Minecraft server running this Wrapper.

## Setup

1. **Ensure Python 3.0 or newer is installed and running on your system.**
   - There are many great YouTube tutorials to help with this.

2. **Copy `Wrapper.py` into your Minecraft folder.**

3. **Open `Wrapper.py` in a text editor to configure the settings.**
   - The options are at the top of the file in the CONFIG section.
   - You can change the Min and Max RAM usage.
   - Set the name of your server jar file (default is `server.jar`).
   - The `KEY` field should be left blank until you run it for the first time. It will provide instructions on what to put there.
   - The port should remain unchanged (default: `25564`) if you plan on using this with the McWrapper Discord bot.

4. **Port Forwarding:**
   - If you are using the Discord bot or plan for this to be accessible outside your local network, make sure to port forward `25564` as well as Minecraft's `25565`.

## Running the Wrapper

1. **Open a command prompt.**

2. **Run the Python script:**
   - Instead of running a `.bat` file or double-clicking the `.jar` file, execute: 
     ```sh
     python3 Wrapper.py
     ```
   - Note: Some installations may use `python` instead of `python3`.

3. **Server Operation:**
   - You will now see the Minecraft server starting up in the command prompt. You can use it like regular, but it will be listening on port `25564` for connections.

## Support

For problems or questions, email me at [socksinthewash@gmail.com](mailto:socksinthewash@gmail.com).
