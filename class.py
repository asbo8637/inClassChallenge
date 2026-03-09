from flask import Flask, request, render_template_string
from pysnmp.hlapi import (
    ObjectType, ObjectIdentity, getCmd, nextCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
)
import os

app = Flask(__name__)


# SNMP configuration (direct to R2)
R2_IP = "172.16.1.2"
SNMP_PORT = 161
COMMUNITY = "public"
TARGET_INTERFACE = "FastEthernet0/0"

MAP_INPUT = {
    "Description": "1.3.6.1.2.1.2.2.1.2",
    "PhysAddress": "1.3.6.1.2.1.2.2.1.6",
    "AdminStatus": "1.3.6.1.2.1.2.2.1.7",
    "InputPackets": "1.3.6.1.2.1.2.2.1.11",
    "OperStatus": "1.3.6.1.2.1.2.2.1.8",
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>R2 Get Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin-left: 180px;
            margin-top: 60px;
        }
        .box {
            border: 1px solid #777;
            width: 500px;
            padding: 16px;
            margin-left: 256px;
            margin-top: 20px;
            font-size: 20px;
        }
        .field {
            margin-top: 30px;
            margin-bottom: 30px;
        }
        label {
            display: block;
            margin-bottom: 12px;
        }
        input[type=text] {
            width: 320px;
            height: 34px;
            font-size: 18px;
            padding: 4px 8px;
        }
        input[type=submit] {
            font-size: 18px;
            padding: 8px 18px;
        }
        .results {
            margin-top: 25px;
            padding: 12px;
            background: #f4f4f4;
        }
        .error {
            color: red;
            margin-top: 20px;
        }
        .hint {
            font-size: 16px;
            color: #333;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <h1>R2 Interface Details</h1>
    <div class="box">
        <div>Enter R2 Fa 0/0's interface details to be fetched:</div>
        <form method="post">
            <div class="field">
                <label>Value1:</label>
                <input type="text" name="value1" value="{{ value1 or '' }}">
            </div>

            <div class="field">
                <label>Value2:</label>
                <input type="text" name="value2" value="{{ value2 or '' }}">
            </div>

            <div class="field">
                <label>Value3:</label>
                <input type="text" name="value3" value="{{ value3 or '' }}">
            </div>

            <input type="submit" value="Submit">
        </form>

        <div class="hint">
            Valid examples: Description, PhysAddress, AdminStatus, InputPackets, OperStatus
        </div>

        {% if results %}
        <div class="results">
            <h3>Results for {{ iface_name }}</h3>
            <ul>
            {% for k, v in results.items() %}
                <li><b>{{ k }}</b>: {{ v }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""



def grab_snmp(oid, port):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(COMMUNITY, mpModel=1),
        UdpTransportTarget((R2_IP, SNMP_PORT), timeout=2, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid)),
    )
    err, stat, idx, binds = next(iterator)
    if err:
        raise RuntimeError(str(err))
    if stat:
        raise RuntimeError(f"{stat.prettyPrint()} at {idx and binds[int(idx) - 1][0] or '?'}")
    for _, val in binds:
        return val.prettyPrint()
    raise RuntimeError("Nothing came back from SNMP")




def get_iface_index(iface_name, port):
    base_oid = "1.3.6.1.2.1.2.2.1.2"  # ifDescr
    for err, stat, idx, binds in nextCmd(
        SnmpEngine(),
        CommunityData(COMMUNITY, mpModel=1),
        UdpTransportTarget((R2_IP, SNMP_PORT), timeout=2, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(base_oid)),
        lexicographicMode=False,
    ):
        if err:
            raise RuntimeError(str(err))
        if stat:
            raise RuntimeError(f"{stat.prettyPrint()} at {idx and binds[int(idx) - 1][0] or '?'}")
        match = next((oid for oid, val in binds if val.prettyPrint() == iface_name), None)
        if match:
            return int(str(match).split(".")[-1])
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    value1 = value2 = value3 = ""

    if request.method == "POST":
        value1 = request.form.get("value1", "").strip()
        value2 = request.form.get("value2", "").strip()
        value3 = request.form.get("value3", "").strip()
        fields = [value1, value2, value3]

        try:
            idx = get_iface_index(TARGET_INTERFACE, SNMP_PORT)
            if idx is None:
                error = f"Couldn't find interface {TARGET_INTERFACE} on R2."
            else:
                results = {}
                for field in fields:
                    if not field:
                        continue
                    oid = OID_MAP.get(field)
                    try:
                        full_oid = f"{oid}.{idx}"
                        results[field] = grab_snmp(full_oid, SNMP_PORT)
                    except Exception as e:
                        results[field] = f"Error: {e}"
        except Exception as e:
            error = str(e)

    return render_template_string(
        HTML,
        results=results,
        error=error,
        value1=value1,
        value2=value2,
        value3=value3,
        iface_name=TARGET_INTERFACE,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)