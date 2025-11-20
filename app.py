from flask import Flask, render_template
from routes.routes import routes
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(routes)

@app.route('/')
def home():
    return render_template('index.html')  

if __name__ == "__main__":
    app.run(debug=True, port=5000)
