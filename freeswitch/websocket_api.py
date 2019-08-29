#!/usr/bin/env python3
import asyncio
import websockets
import json
import signal

content = ''


def read_wav(filename):
    with open(filename, mode='rb') as file:
        content = file.read()
        return content


@asyncio.coroutine
def request_content(content):
    hypothesis = ''
    websocket = yield from websockets.connect('ws://asr2.openfpt.vn/ws')
    # with websockets.connect('ws://asr2.openfpt.vn/ws') as websocket:
    yield from websocket.send(content)
    yield from websocket.send("EOS")
    while True:
        result = yield from websocket.recv()
        j = json.loads(result)
        if 'result' not in result:
            continue
        hypothesis = j['result']['hypotheses'][0]['transcript']
        print(hypothesis)
        if (j['result']['final']): break
    websocket.close()
    return hypothesis


def get_websocket_result(filename):
    result = ''
    loop = asyncio.get_event_loop()
    content = read_wav(filename)
    try:
        result = loop.run_until_complete(request_content(content))
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.wait(list(pending)))
    except websockets.exceptions.ConnectionClosed as e:
        # print (e)
        print("Connection closed")
    finally:
        loop.close()
        return result


if __name__ == "__main__":
    get_websocket_result('/home/hieung1707/python_code/voice_detection/tongdai.wav')




