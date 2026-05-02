import os
import re
from functools import wraps

import jwt
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"reveal system prompt",
    r"bypass security",
    r"drop\s+table",
    r"or\s+1=1",
    r"<script.*?>"
]

def sanitize_input(user_input):

    # Empty input check
    if not user_input or not user_input.strip():
        return False, "Input cannot be empty"

    # HTML detection (strip/block)
    if re.search(r"<[^>]+>", user_input):
        return False, "HTML content is not allowed"

    # Prompt injection detection
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Potential malicious input detected"

    return True, "Valid input"

# from services.rate_limiting import setup_rate_limiting

JWT_SECRET = os.getenv('JWT_SECRET', 'change-me-set-a-secure-32-byte-secret!')

app = Flask(__name__)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)

Talisman(
    app,
    content_security_policy={"default-src": ["'self'"]},
    force_https=False,
    strict_transport_security=True,
    strict_transport_security_preload=True,
    strict_transport_security_max_age=31536000,
    content_security_policy_nonce_in=['script-src']
)


def requires_jwt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(' ', 1)[1].strip()
        try:
            jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return wrapper

@app.route('/test', methods=['GET'])
def test():
    return "OK"

@app.route('/describe', methods=['POST'])
@requires_jwt
def describe_endpoint():
    data = request.get_json()
    prompt = data.get("prompt", "")

    # 👇 YOUR CODE GOES HERE
    valid, message = sanitize_input(prompt)

    if not valid:
        return jsonify({
            "error": message
        }), 400

    # continue normal AI logic
    return jsonify({"message": "Prompt processed successfully"}), 200

@app.route('/generate-report', methods=['POST'])
@limiter.limit("10 per minute")
@requires_jwt
def generate_report():
    # Placeholder for generate report logic
    return {"message": "Report generated"}, 200

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)