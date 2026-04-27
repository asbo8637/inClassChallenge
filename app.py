from flask import Flask, render_template_string
import subprocess

app = Flask(__name__)

R3_LOOPBACK_IP = "100.0.0.1"
SOURCE_IP = "198.51.100.21"
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
    return render_template_string(
        HTML,
        output=""
    )

@app.route("/traceroute", methods=["POST"])
def traceroute():
    try:
        command = [
            "traceroute",
            "-i", INTERFACE,
            "-s", SOURCE_IP,
            R3_LOOPBACK_IP
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=45
        )

        output = "$ " + " ".join(command) + "\n\n"
        output += result.stdout

        if result.stderr:
            output += "\nSTDERR:\n" + result.stderr

    except subprocess.TimeoutExpired:
        output = "Traceroute timed out."
    except FileNotFoundError:
        output = "traceroute is not installed. Run: sudo apt install traceroute"
    except Exception as e:
        output = f"Error: {e}"

    print(output)

    return render_template_string(HTML, output=output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)