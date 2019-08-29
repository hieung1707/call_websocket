#!/usr/bin/env python3
import asyncio
import websockets
import json
import sys
import time


content = ''

async def request_content(content):
    hypothesis = ''
    async with websockets.connect('ws://asr2.openfpt.vn/ws') as websocket:
        # sys.stdout.write('VERBOSE \"{}\"\n'.format('begin to call websocket api'))
        # sys.stdout.flush()
        await websocket.send(content)
        await websocket.send("EOS")
        while True:
            result = await websocket.recv()
            j = json.loads(result)
            if 'result' not in result:
                continue
            hypothesis = j['result']['hypotheses'][0]['transcript']
            print(hypothesis)
            # sys.stdout.write('VERBOSE \"{}\"\n'.format(j['result']['hypotheses'][0]['transcript']))
            # sys.stdout.flush()
            if (j['result']['final']): break
    return hypothesis
        # sys.stdout.write('VERBOSE \"{}\"\n'.format('done recognizing'))
        # sys.stdout.flush()


def get_websocket_result(content):
    try:
        asyncio.get_event_loop().run_until_complete(request_content(content))
    except websockets.exceptions.ConnectionClosed as e:
        print (e)

if __name__ == "__main__":
    with open('/home/hieung1707/python_code/voice_detection/tongdai.wav', mode='rb') as file:
        content = file.read()
    get_websocket_result(content)




