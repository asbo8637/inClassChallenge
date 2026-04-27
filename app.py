from flask import Flask, render_template_string
import subprocess

app = Flask(__name__)

R3_LOOPBACK_IP = "100.0.0.1"
INTERFACE = "tap0"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Button Things</title>
</head>
<body>
    <form method="post" action="/traceroute">
        <button type="submit">Traceroute to 100.0.0.1</button>
    </form>
    <pre>{{ output }}</pre>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML, output="")

@app.route("/traceroute", methods=["POST"])
def traceroute():
    try:
        command = [
            "traceroute",
            "-i", INTERFACE,
            R3_LOOPBACK_IP
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=45
        )

        output = result.stdout

    return render_template_string(HTML, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)