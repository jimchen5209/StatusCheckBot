from flask import Flask
from gevent.pywsgi import WSGIServer
import status

app = Flask(__name__)

@app.route('/getStatus', methods=['GET'])
def index():
    return status.getStatus()

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
