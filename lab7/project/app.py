from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Background thread to update the file and emit data to the frontend
def read_file_and_emit():
    while True:
        with open('/home/student/CSCI_5280_SDN/lab7/data.txt', 'r') as f:
            data = [float(line.strip()) for line in f]
        
        socketio.emit('update_data', {'data': data})
        
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

# Start the background thread when the server starts
@socketio.on('connect')
def start_background_thread():
    threading.Thread(target=read_file_and_emit).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)

