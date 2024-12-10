from flask import Flask, request, jsonify, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.json
    topic = data.get('topic', '')
    problems = data.get('problems', '')

    # Use subprocess to simulate terminal commands
    try:
        # Example: Call your story generation script with inputs
        result = subprocess.check_output(
            ['python', 'storyGenerator.py'],
            input=f"{topic}\n{problems}\n",
            text=True
        )
        return jsonify({"output": result.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output}), 500

@app.route('/replace_synonyms', methods=['POST'])
def replace_synonyms():
    try:
        result = subprocess.check_output(['python', 'replace_synonyms.py'], text=True)
        return jsonify({"output": result.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output}), 500

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    input_text = data.get('text', '')

    # Example: Pass the input text to a script
    try:
        result = subprocess.check_output(
            ['python', 'dictionaryParser.py'],
            input=input_text,
            text=True
        )
        return jsonify({"output": result.strip()})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output}), 500

if __name__ == '__main__':
    app.run(debug=True)
