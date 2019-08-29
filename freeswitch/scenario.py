#!/usr/bin/python
# -*- coding: utf-8 -*-
from tempfile import mkstemp
from websocket_api import get_websocket_result
from freeswitch import *


def handler(session, *args):
    # session.answer()
    timeout = 6
    base_energy = 500
    sil = 1
    caller_id = 1000
    caller_id = session.getVariable('callerid')
    filepath = ''
    filepath = session.getVariable('filepath')
    timeout = int(session.getVariable('timeout'))
    base_energy = int(session.getVariable('base_energy'))
    sil = int(session.getVariable('sil'))
    session.execute('playback', filepath)
    tmp_filename = 'TmpSpeechFile_{}.wav'.format(caller_id)
    _, temp_sound_file = mkstemp(tmp_filename)
    session.recordFile(tmp_filename, timeout, base_energy, sil)
    result = get_websocket_result(tmp_filename)
    consoleLog('Result:{}'.format(result))
    session.hangup()