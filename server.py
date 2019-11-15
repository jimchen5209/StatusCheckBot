from flask import Flask
import status

app = Flask(__name__)

@app.route('/getStatus')
def index():
    return status.getStatus()

if __name__ == '__main__':
    app.run()
