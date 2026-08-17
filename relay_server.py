#!/usr/bin/env python3
"""
TCP relay to bridge Docker container and WSL2 host network.
Listens on 0.0.0.0:8765 (all interfaces) and forwards to 127.0.0.1:8766
where our actual server runs.
"""
import socket
import threading
import select

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8765
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 8766

def relay(src, dst, prefix):
    """Copy data between sockets until one closes."""
    try:
        while True:
            ready, _, _ = select.select([src], [], [], 1.0)
            if not ready:
                if src.fileno() == -1:
                    break
                continue
            try:
                data = src.recv(8192)
            except:
                break
            if not data:
                break
            try:
                dst.sendall(data)
            except:
                break
    except:
        pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def handle_client(client_sock):
    """Handle a single client connection."""
    try:
        target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_sock.connect((TARGET_HOST, TARGET_PORT))
        threading.Thread(target=relay, args=(client_sock, target_sock, "C->S"), daemon=True).start()
        threading.Thread(target=relay, args=(target_sock, client_sock, "S->C"), daemon=True).start()
    except Exception as e:
        print(f"Relay error: {e}")
        try: client_sock.close()
        except: pass

def main():
    # First, start our actual server on port 8766
    import subprocess
    import os
    
    # Kill any existing servers
    os.system("pkill -f doc_reader_tk 2>/dev/null")
    import time
    time.sleep(2)
    
    # Start the doc reader server on port 8766
    server_proc = subprocess.Popen([
        "/opt/data/.venv-docreader/bin/python3",
        "/opt/data/doc_reader_tk.py",
        "--api-server", "8766"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(3)
    
    # Verify the target server is running
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect(("127.0.0.1", 8766))
        s.close()
        print("Target server on port 8766 is running")
    except:
        print("ERROR: Target server on port 8766 is not running!")
        return
    
    # Now start the relay server on port 8765
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(50)
    print(f"Relay server listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"  Forwarding to {TARGET_HOST}:{TARGET_PORT}")
    print(f"  Try accessing: http://localhost:8765 or http://172.17.0.2:8765")
    
    while True:
        try:
            client_sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
        except KeyboardInterrupt:
            print("\nShutting down relay...")
            server_proc.terminate()
            break
        except:
            pass

if __name__ == "__main__":
    main()
