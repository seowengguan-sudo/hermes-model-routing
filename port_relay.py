#!/usr/bin/env python3
"""
TCP port relay: Bridges external connections to the document reader API.
Since we can't install socat or use SSH, this Python relay provides
the same functionality.
"""
import socket
import select
import threading
import sys

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8765
TARGET_HOST = "127.0.0.1"
TARGET_PORT = 8765

def relay(conn, addr):
    """Relay data between client and target server."""
    try:
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect((TARGET_HOST, TARGET_PORT))
        
        sockets = [conn, target]
        while True:
            r, _, _ = select.select(sockets, [], [], 1.0)
            if not r:
                continue
            for s in r:
                data = s.recv(4096)
                if not data:
                    return
                if s is conn:
                    target.sendall(data)
                else:
                    conn.sendall(data)
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except:
            pass
        try:
            target.close()
        except:
            pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(5)
    print(f"Port relay: {LISTEN_HOST}:{LISTEN_PORT} -> {TARGET_HOST}:{TARGET_PORT}")
    
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=relay, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    main()
