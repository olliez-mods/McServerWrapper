
# ========================================- [CONFIG] -========================================
# Ram min and max, in mb
RAM_MIN_MB = 500
RAM_MAX_MB = 800

# Name of the server jar file
SERVER_FILE_NAME = "server.jar"

# The key for verification, to get a new one set this as a blank string and run the program (it is a uuid4 string)
KEY = "94c5cdfc02444871972f59c31e24b885"

# Port, what port should we listen on, (The discord bot will ALWAYS try and reach us on 25564)
PORT = 25564
# ============================================================================================










import io
import subprocess
import threading
import time
import socket
import select
import re
from typing import Optional, Any
import uuid

def generate_key():
    return str(uuid.uuid4()).replace("-", "")
def read_next_kv(p:list[str]):
    if(len(p) < 2):
        return None, None
    k = p.pop(0)
    v = p.pop(0)
    return k, v
def verify_packet(p:str) -> Optional[list[str]]:
    lis = p.split("<#?=~>")
    length = len(lis)
    if(length == 0 or length == 0 or length%2 != 0):
        return None
    return lis
def can_recv(s:socket.socket):
    r = select.select([s], [], [], 0.5)
    return r[0]
def snd(sock: socket.socket, address: tuple[Any, ...], string: str):
    sock.sendto(string.encode(), address)
def prnt_cap(include_head:bool = False):
    if(include_head): print("=============== [MC Wrapper] ===============", flush=True)
    else:             print("============================================", flush=True)
def prnt(msg:str, end:str = "\n"):
    print(f"[MC Wrapper] - {msg}", flush=True, end=end)

def read_out_stream(process:subprocess.Popen, chat_stream:io.StringIO):
    chat_pattern = re.compile(r"\[.*\].*<(.+?)> (.+)")
    while(True):
        output = process.stdout.readline()
        if output:
            print(output, end="", flush=True)
            match = chat_pattern.search(output)
            if(match and not "<#?=~>" in match.group(2)):
                prnt(f"Putting a message in: {match.group(2)}")
                chat_stream.write("<#?=~>")
                chat_stream.write(match.group(1))
                chat_stream.write("<#?=~>")
                chat_stream.write(match.group(2))
        else: break

def read_in_stream(process:subprocess.Popen):
    try:
        while True:
            command = input()
            process.stdin.write(f"{command}\n")
            process.stdin.flush()
    except KeyboardInterrupt:
        prnt("Exiting input stream because of Ctrl+C")
    except EOFError:
        prnt("Exiting input stream because of Ctrl+C")


if(KEY == "" or len(KEY) != 32 or not KEY.isalnum()):
    print("========================================")
    print("\nNo valid KEY found, please use:")
    print(f"\"{generate_key()}\"")
    print("as a new key.")
    print("Open \"Wrapper.py\" and paste your new key into")
    print("the key field in the CONFIG section at the top\n")
    print("========================================")
    exit()

prnt("Starting MC Server...")
mc_process = subprocess.Popen(['java', f'-Xmx{RAM_MAX_MB}M', f'-Xms{RAM_MIN_MB}M', '-jar', f'{SERVER_FILE_NAME}', 'nogui'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

chat_stream = io.StringIO()

# Cursur position for chat_stream
c_pos = 0

output_thread = threading.Thread(target=read_out_stream, args=(mc_process, chat_stream), daemon=True)
output_thread.start()

input_thread = threading.Thread(target=read_in_stream, args=(mc_process,), daemon=True)
input_thread.start()


try:
# MAIN PROGRAM =====================================================================================
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    sock.bind(('127.0.0.1', PORT))
    prnt(f"Listening on port {{{PORT}}}")
    while True:
        if(can_recv(sock)):
            try:
                data, addr = sock.recvfrom(1024)
                p = verify_packet(data.decode())
                if(p == None):
                    snd(sock, addr, "BAD PACKET")
                    continue

                key, value = read_next_kv(p)
                if(key == "ping"):
                    snd(sock, addr, "pong")
                    continue
                elif(key == "status"):
                    snd(sock, addr, "NOT SUPPORTED YET")
                    continue
                elif(key == "key"):
                    if(value != KEY):
                        snd(sock, addr, "BAD KEY")
                        continue
                else:
                    snd(sock, addr, f'Unknown "{key}"')
                    continue
                snd(sock, addr, "LOGGED IN")
                # If we get here, assume correct login
                key, value = read_next_kv(p)
                if(key == None): continue

                if(key == "SAY"):
                    mc_process.stdin.write(f'tellraw @a \"{value}\"\n')
                    mc_process.stdin.flush()
                    snd(sock, addr, "DONE")
                    continue
                if(key == "GET-CHAT"):
                    chat_stream.seek(c_pos)
                    chat_str = chat_stream.read()
                    c_pos += len(chat_str)

                    num_messages = int(chat_str.count("<#?=~>"))
                    if(num_messages > 0): num_messages = int(num_messages/2)

                    #chat_str should start with a seperator
                    snd(sock, addr, f"CHAT<#?=~>{num_messages}{chat_str} ")
                    continue

                if(key == "COMMAND"):
                    mc_process.stdin.write(f"{value}")
                    mc_process.stdin.flush()
                    snd(sock, addr, "DONE")
                    continue

                snd(sock, addr, "END")
            except Exception as e:
                prnt(f"We got an error:\n{e}")
        else:
            time.sleep(0.1)
# ==================================================================================================
except KeyboardInterrupt:
    # Handle Ctrl-C for graceful shutdown
    prnt("Stopping main thread because of Ctrl+C")
finally:
    # Ensure the subprocess does not become a zombie
    prnt("Stopping MC Server gracefully...")
    while(True):
        try:
            #mc_process.communicate()
            break
        except KeyboardInterrupt:
            prnt("Please allow Minecraft server to stop before exiting the wrapper")

prnt("Goodbye :D")
