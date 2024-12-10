from flask import Flask, send_from_directory
from api.download import app as api_app  # Importing the blueprint from api.download

app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(api_app, url_prefix='/api')

# Serve the index.html page from the static folder
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Listening on port 8080
