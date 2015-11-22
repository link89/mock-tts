from flask import Flask
from flask_restful import Api

from resources.tts import Tts

app = Flask(__name__.split('.')[0])

api = Api(app)

@api.representation('audio/wav')
def output_wav(data, code, headers = None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp

api.add_resource(Tts, '/v1/tts')
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug=True)
