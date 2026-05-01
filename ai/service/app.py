from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.describe import describe
from services.rate_limiting import setup_rate_limiting

app = Flask(__name__)

# Setup rate limiting
limiter = setup_rate_limiting(app)

@app.route('/describe', methods=['POST'])
def describe_endpoint():
    return describe()

@app.route('/generate-report', methods=['POST'])
@limiter.limit("10 per minute")
def generate_report():
    # Placeholder for generate report logic
    return {"message": "Report generated"}, 200

if __name__ == '__main__':
    app.run(debug=True)