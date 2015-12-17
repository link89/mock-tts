from flask_restful import Resource, reqparse, fields, marshal_with
from flask import make_response
from cStringIO import StringIO
import os, wave, json, re

def load_media(path):
    media = {}
    for f in os.listdir(path):
        name, ext = os.path.splitext(f)
        wav = wave.open(os.path.join(path, f), 'r')
        media[name] = wav.readframes(wav.getnframes())
        wav.close()
    return media

class Tts(Resource):
    sampleRate = 8000   # sample rate in Hz
    sampleWidth = 2     # sample width in byte
    channel = 1

    commonPath = './media/common'
    customPath = './media/custom'
    common = load_media(commonPath)
    custom = load_media(customPath)

    parser = reqparse.RequestParser()
    parser.add_argument('text', location = 'json', required = True)

    @classmethod
    def gap_to_wav(cls, token):
         return '\0' * cls.sampleWidth * int(cls.sampleRate / 1000.0 * int(token))

    @classmethod
    def digits_and_letters_to_wav(cls, token):
        wav = ''
        for c in token:
            wav += cls.common.get(c)
        return wav

    @classmethod
    def pre_recording_to_wav(cls, token):
        wav = cls.custom.get(token)
        if wav:
            return wav
        else:
            return ''

    @classmethod
    def money_to_wav(cls, token):
        return ''

    def post(self):
        args = Tts.parser.parse_args()
        text = args['text']
        pattern = (r"\((.*?)\)|"    # match string between ()
                   r"\[(.*?)\]|"    # match string between []
                   r"\{(.*?)\}|"    # match string between {}
                   r"\$(.*?)\$")    # match string between $$
        tokens = re.findall(pattern, text)

        def token_to_wav(token):
            if token[0]:
                return Tts.gap_to_wav(token[0])
            elif token[1]:
                return Tts.digits_and_letters_to_wav(token[1])
            elif token[2]:
                return Tts.pre_recording_to_wav(token[2])
            elif token[3]:
                return Tts.money_to_wav(token[3])
            else:
                return ''

        wav = ''
        for token in tokens:
            wav += token_to_wav(token)

        wavBuf = StringIO()
        wavFd = wave.open(wavBuf, 'w')
        wavFd.setparams((Tts.channel, Tts.sampleWidth, Tts.sampleRate, len(wav)/Tts.sampleWidth, 'NONE', 'not compressed' ))
        wavFd.writeframes(wav)
        wavFd.close()
        wavStr = wavBuf.getvalue()
        wavBuf.close()

        resp = make_response(wavStr)
        resp.headers['Content-Type'] = 'audio/wav'
        resp.headers['Content-Disposition'] = 'attachment; filename=sound.wav'
        return resp
