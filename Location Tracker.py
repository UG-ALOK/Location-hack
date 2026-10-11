
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LOCATION LAB — Localhost Location Report
For personal testing and consenting users.
"""

import os
import sys
import time
import json
import math
import socket
import threading
import webbrowser
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from flask import Flask, request, jsonify, render_template_string

# ================= COLORS =================

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4096

# ================= WEB PAGE =================

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Location Lab</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 20px;
    color: #edf4ff;
    background:
        radial-gradient(ellipse at 50% 0%, #12304b, transparent 55%),
        #060910;
    font-family: "Trebuchet MS", "Segoe UI", system-ui, sans-serif;
}

.panel {
    width: 100%;
    max-width: 430px;
    padding: 28px 22px;
    border: 1px solid #263b50;
    border-radius: 18px;
    background: #0e1522;
    box-shadow: 0 15px 45px #0008;
    text-align: center;
}

.brand {
    color: #41e8ff;
    font-size: 12px;
    letter-spacing: 3px;
    font-weight: bold;
}

h1 {
    font-size: 28px;
    margin: 12px 0 5px;
}

.subtitle {
    color: #91a4bd;
    font-size: 13px;
    line-height: 1.7;
}

.globe-wrap {
    position: relative;
    width: 165px;
    height: 165px;
    margin: 24px auto;
    display: grid;
    place-items: center;
}

.globe {
    width: 125px;
    height: 125px;
    border: 1px solid #41e8ff88;
    border-radius: 50%;
    background:
        repeating-linear-gradient(
            90deg,
            transparent 0 17px,
            #41e8ff55 18px 19px,
            transparent 20px 35px
        ),
        repeating-linear-gradient(
            0deg,
            #0d2840,
            #123e56 12px,
            #071321 24px
        );
    box-shadow: 0 0 30px #41e8ff33;
    animation: rotate 9s linear infinite, float 4s ease-in-out infinite;
}

.orbit {
    position: absolute;
    width: 165px;
    height: 58px;
    border: 1px solid #a78bfa99;
    border-radius: 50%;
    transform: rotate(-28deg);
}

@keyframes rotate {
    from { background-position: 0 0; }
    to { background-position: 70px 0; }
}

@keyframes float {
    0%, 100% { translate: 0 0; }
    50% { translate: 0 -6px; }
}

.card {
    padding: 20px;
    text-align: left;
    border: 1px solid #263b50;
    border-radius: 14px;
    background: #111d2c;
}

.card h2 {
    font-size: 16px;
    margin: 0 0 10px;
    color: #41e8ff;
}

.card p {
    color: #a8b8cc;
    font-size: 12px;
    line-height: 1.8;
}

.notice {
    margin-top: 16px;
    padding: 12px;
    border: 1px solid #51452a;
    border-radius: 10px;
    background: #211b10;
    color: #e9d6ad;
    font-size: 11px;
    line-height: 1.8;
    text-align: left;
}

button {
    width: 100%;
    padding: 14px;
    margin-top: 10px;
    border: 1px solid #45f5a155;
    border-radius: 10px;
    background: #103526;
    color: #45f5a1;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 1px;
    cursor: pointer;
}

button:disabled {
    opacity: .55;
    cursor: wait;
}

#status {
    margin-top: 15px;
    color: #91a4bd;
    font-size: 12px;
    line-height: 1.8;
    overflow-wrap: anywhere;
}

footer {
    margin-top: 22px;
    color: #718198;
    font-size: 10px;
    letter-spacing: 1px;
}
</style>
</head>

<body>
<div class="panel">
    <div class="brand">◈ LOCATION LAB</div>
    <h1>Location Scanner</h1>
    <div class="subtitle">
        Localhost location testing dashboard
    </div>

    <div class="globe-wrap">
        <div class="orbit"></div>
        <div class="globe"></div>
    </div>

    <div class="card">
        <h2>◎ LOCATION SCAN</h2>
        <p>
            Press the button to request your browser's location
            permission. After you allow it, the address report
            will be generated in your Termux terminal.
        </p>
        <button id="location-btn" onclick="startLocation()">
            ⌖ SCAN LOCATION
        </button>
        <div id="status" aria-live="polite"></div>
    </div>

    <div class="notice">
        <strong>PRIVACY NOTICE</strong><br>
        Location is requested only after you press the button
        and grant permission. Coordinates are sent to this local
        server and OpenStreetMap Nominatim to resolve the address.
        Detailed results appear in Termux. Continue only if you agree.
    </div>

    <footer>LOCALHOST ONLY · PERSONAL TESTING</footer>
</div>

<script>
const statusBox = document.getElementById("status");
const button = document.getElementById("location-btn");

function setStatus(text, color) {
    statusBox.textContent = text;
    statusBox.style.color = color || "#91a4bd";
}

function startLocation() {
    if (!navigator.geolocation) {
        setStatus("Geolocation is not supported.", "#ff707b");
        return;
    }

    button.disabled = true;
    setStatus("Waiting for your permission…", "#ffc56b");

    const start = performance.now();

    navigator.geolocation.getCurrentPosition(
        async function(position) {
            setStatus("Location received. Sending to Termux…", "#ffc56b");

            try {
                const response = await fetch("/location", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        acquisition_ms: Math.round(performance.now() - start)
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error("Report generation failed");
                }

                setStatus(
                    "100% Send Complete — Location check your Termux report screen.",
                    "#45f5a1"
                );
                button.textContent = "SEND COMPLETE";
            } catch (error) {
                setStatus(
                    "Send failed. Check Termux and retry.",
                    "#ff707b"
                );
                button.disabled = false;
            }
        },
        function(error) {
            const messages = {
                1: "Permission denied. No location was sent.",
                2: "Location unavailable. Check device settings.",
                3: "Location request timed out. Please retry."
            };

            setStatus(
                messages[error.code] || "Unable to get location.",
                "#ff707b"
            );
            button.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 60000,
            maximumAge: 0
        }
    );
}
</script>
</body>
</html>
"""

# ================= SECURITY HEADERS =================

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "geolocation=(self)"
    return response

@app.get("/")
def home():
    return render_template_string(PAGE)

# ================= REVERSE GEOCODING =================

last_lookup = 0.0

def reverse_geocode(latitude, longitude):
    global last_lookup

    # Respect the public Nominatim usage limit.
    wait = 1.1 - (time.monotonic() - last_lookup)
    if wait > 0:
        time.sleep(wait)

    params = urlencode({
        "format": "jsonv2",
        "lat": str(latitude),
        "lon": str(longitude),
        "zoom": "18",
        "addressdetails": "1"
    })

    url = "https://nominatim.openstreetmap.org/reverse?" + params

    req = Request(
        url,
        headers={
            "User-Agent": "LocationLab/1.0 (personal localhost testing)",
            "Accept": "application/json"
        }
    )

    with urlopen(req, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))

    last_lookup = time.monotonic()

    if not isinstance(result, dict):
        raise ValueError("Invalid address response")

    return result

# ================= SINGLE GREEN REPORT =================

def print_report(latitude, longitude, accuracy, acquisition_ms,
                 received_at, lookup_seconds, total_seconds, result):

    address = result.get("address") or {}
    full_address = result.get("display_name") or "Address not resolved"

    width = 60

    def row(text=""):
        text = str(text)
        available = width - 4

        while len(text) > available:
            print(f"{GREEN}│ {text[:available]:<{available}} │{RESET}")
            text = text[available:]

        print(f"{GREEN}│ {text:<{available}} │{RESET}")

    os.system("clear")

    print(f"{GREEN}{BOLD}╭{'─' * (width - 2)}╮{RESET}")
    row("             LOCATION REPORT")
    print(f"{GREEN}├{'─' * (width - 2)}┤{RESET}")

    row("FULL ADDRESS")
    for part in full_address.split(", "):
        row(part)

    print(f"{GREEN}├{'─' * (width - 2)}┤{RESET}")
    row("ADDRESS DETAILS")

    fields = [
        ("House number", "house_number"),
        ("Road", "road"),
        ("Neighbourhood", "neighbourhood"),
        ("Suburb", "suburb"),
        ("City", "city"),
        ("Town", "town"),
        ("Village", "village"),
        ("District", "county"),
        ("State", "state"),
        ("Postcode", "postcode"),
        ("Country", "country"),
    ]

    shown = set()
    for label, key in fields:
        value = address.get(key)
        if value and value not in shown:
            row(f"{label}: {value}")
            shown.add(value)

    print(f"{GREEN}├{'─' * (width - 2)}┤{RESET}")
    row("COORDINATES")
    row(f"Latitude: {latitude:.7f}")
    row(f"Longitude: {longitude:.7f}")
    row(f"Accuracy: +/- {accuracy:.1f} metres")

    print(f"{GREEN}├{'─' * (width - 2)}┤{RESET}")
    row("TIMING")
    row(f"Received: {received_at}")
    row(f"Browser acquisition: {acquisition_ms / 1000:.2f} sec")
    row(f"Address lookup: {lookup_seconds:.2f} sec")
    row(f"Server processing: {total_seconds:.2f} sec")
    row(f"Processing minutes: {total_seconds / 60:.4f}")

    print(f"{GREEN}├{'─' * (width - 2)}┤{RESET}")
    row("Status: SUCCESS")
    row("Report displayed in Termux; not saved to disk")
    print(f"{GREEN}╰{'─' * (width - 2)}╯{RESET}")

# ================= LOCATION ENDPOINT =================

@app.post("/location")
def receive_location():
    request_start = time.perf_counter()
    received_at = now_text()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(success=False), 400

    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])
        accuracy = float(data.get("accuracy", 0))
        acquisition_ms = float(data.get("acquisition_ms", 0))
    except (KeyError, TypeError, ValueError):
        return jsonify(success=False), 400

    values = (latitude, longitude, accuracy, acquisition_ms)
    if not all(math.isfinite(value) for value in values):
        return jsonify(success=False), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify(success=False), 400

    if accuracy < 0 or acquisition_ms < 0:
        return jsonify(success=False), 400

    print(f"\n{CYAN}[+] Authorized location received.{RESET}")
    print(f"{CYAN}[+] Resolving address…{RESET}")

    lookup_start = time.perf_counter()

    try:
        result = reverse_geocode(latitude, longitude)
        lookup_seconds = time.perf_counter() - lookup_start
        total_seconds = time.perf_counter() - request_start

        print_report(
            latitude,
            longitude,
            accuracy,
            acquisition_ms,
            received_at,
            lookup_seconds,
            total_seconds,
            result
        )

        return jsonify(success=True)

    except Exception as error:
        print(f"{RED}[!] Address lookup failed: {type(error).__name__}{RESET}")
        print(f"{YELLOW}Check internet access and try again later.{RESET}")
        return jsonify(success=False), 502

# ================= MENU =================

def now_text():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

def banner():
    os.system("clear")
    print(f"""{CYAN}{BOLD}
╔══════════════════════════════════════════════════╗
║                 LOCATION LAB                     ║
║             LOCALHOST REPORT TOOL                ║
╚══════════════════════════════════════════════════╝
{RESET}""")

def port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False

def start_website():
    banner()
    raw = input(f"{YELLOW}[?] Port (Enter = 8080): {RESET}").strip()

    if not raw:
        port = 8080
    elif raw.isdigit() and len(raw) == 4:
        port = int(raw)
    else:
        print(f"{RED}[!] Enter exactly four digits, e.g. 8080.{RESET}")
        return

    if not 1024 <= port <= 9999:
        print(f"{RED}[!] Port must be between 1024 and 9999.{RESET}")
        return

    if not port_available(port):
        print(f"{RED}[!] Port is already in use.{RESET}")
        return

    url = f"http://127.0.0.1:{port}"

    print(f"{GREEN}[+] Starting Location Lab…{RESET}")
    print(f"{CYAN}[+] Open: {url}{RESET}")
    print(f"{YELLOW}[!] Keep Termux open. Press CTRL+C to stop.{RESET}")

    threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    try:
        app.run(
            host="127.0.0.1",
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Server stopped.{RESET}")

def main_menu():
    while True:
        banner()
        print(f"{GREEN}[1]{WHITE}  Location ")
        print(f"{RED}[2]{WHITE} Exit")
        print(f"{GRAY}{'─' * 50}{RESET}")

        choice = input(f"{YELLOW}[?] Select: {RESET}").strip()

        if choice == "1":
            start_website()
            input(f"\n{GRAY}Press Enter to return to menu…{RESET}")
        elif choice == "2":
            print(f"{GREEN}Goodbye!{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}Invalid option.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Stopped by user.{RESET}")
