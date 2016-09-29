#!/usr/bin/python
import websocket
import thread
import time
import arrow

def on_message(ws, message):
    print message

def on_error(ws, error):
    print error

def on_close(ws):
    print "### closed ###"

def on_open(ws):
    def run(*args):
        ws.send('{"type": "auth", "time": arrow.get().timestamp, "source": "560dcedd02b9d75f7e663653", "message": "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJnZW5lcmF0aW9uIjogMCwgInVzZXJfaWQiOiAiNTYwZGNlZGQwMmI5ZDc1ZjdlNjYzNjUzIiwgImV4cCI6IDE0NzUxNzAwNDR9.kfwcNayFTs0OdLcgcf3ydpnz7r1VeS_AlcCREddfSNk"}')
        time.sleep(5)
        for i in range(10):
            time.sleep(10)
            ws.send('{"type": "ping", "time": 1475166494, "source": "560dcedd02b9d75f7e663653", "to": "server", "message": "ping"}')
        time.sleep(1)
        ws.close()
        print "thread terminating..."
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api-virtumedix-vm2.nimaws.com/notifications/tcs.virtumedix.web.4.A9Pq0okYxe9y97crtT2MX2xslhA",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
