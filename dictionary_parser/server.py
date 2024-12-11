from flask import Flask, render_template, Response, request, session, jsonify
import subprocess
import threading
import queue

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Store subprocess and queues globally
process = None
output_queue = queue.Queue()

# Function to read stdout and enqueue it
def read_process_output(proc):
    for line in iter(proc.stdout.readline, ''):
        output_queue.put(line)
    proc.stdout.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_process', methods=['POST'])
def start_process():
    global process, output_queue

    # Start the subprocess for main.py
    if not process:
        process = subprocess.Popen(
            ['python', 'main.py'],  # Replace 'main.py' with your script name
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Start a thread to read the output
        threading.Thread(target=read_process_output, args=(process,), daemon=True).start()
        return jsonify({"status": "Process started"})
    return jsonify({"status": "Process already running"})

@app.route('/send_input', methods=['POST'])
def send_input():
    global process
    user_input = request.json.get('input', '')

    if process:
        # Send user input to the process
        process.stdin.write(user_input + '\n')
        process.stdin.flush()
        return jsonify({"status": "Input sent"})
    return jsonify({"error": "Process not running"})

@app.route('/stream_output')
def stream_output():
    def generate():
        while True:
            try:
                # Get lines from the queue and yield them
                line = output_queue.get(timeout=1)
                yield f"data: {line}\n\n"
            except queue.Empty:
                if process.poll() is not None:
                    break  # Exit if the process is terminated
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stop_process', methods=['POST'])
def stop_process():
    global process
    if process:
        process.terminate()
        process = None
        return jsonify({"status": "Process terminated"})
    return jsonify({"error": "Process not running"})

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
