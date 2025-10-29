from . import __version__
import time

start_time = time.time()

status_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DELPHADEX - Koyeb</title>
    <style>
        body {{
            background-color: #121212;
            color: #00f7ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background-color: #1e1e1e;
            padding: 2rem 3rem;
            border-radius: 16px;
            box-shadow: 0 0 20px rgba(0, 247, 255, 0.4);
            text-align: center;
        }}
        .title {{
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }}
        .version, .uptime {{
            font-size: 1.2rem;
            color: #cccccc;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="title">DELPHADEX Positive Health Emitter</div>
        <div class="version">Version {version}</div>
        <div class="uptime">Uptime: <span id="uptime"></span></div>
    </div>

    <script>
        let uptimeSeconds = {uptime_seconds};
        
        function pad(num) {{
            return num.toString().padStart(2, '0');
        }}

        function updateUptime() {{
            uptimeSeconds++;
            let days = Math.floor(uptimeSeconds / 86400);
            let hours = Math.floor((uptimeSeconds % 86400) / 3600);
            let minutes = Math.floor((uptimeSeconds % 3600) / 60);
            let seconds = uptimeSeconds % 60;
            
            let parts = [];
            
            if (days) {{
                parts.push(`${{days}}d`);
                parts.push(`${{pad(hours)}}h`);
                parts.push(`${{pad(minutes)}}m`);
                parts.push(`${{pad(seconds)}}s`);
            }} else if (hours) {{
                parts.push(`${{hours}}h`);
                parts.push(`${{pad(minutes)}}m`);
                parts.push(`${{pad(seconds)}}s`);
            }} else if (minutes) {{
                parts.push(`${{minutes}}m`);
                parts.push(`${{pad(seconds)}}s`);
            }} else {{
                parts.push(`${{seconds}}s`);
            }}
            
            document.getElementById("uptime").textContent = parts.join(" ");
        }}
        
        updateUptime();
        setInterval(updateUptime, 1000);
    </script>
</body>
</html>
"""

def emit_positive_health(host="0.0.0.0", port=8000, route="/"):
    from flask import Flask
    import threading
    
    app = Flask(__name__)
    
    @app.route(route)
    def ahh():
        uptime_seconds = int(time.time() - start_time)
        return status_html_template.format(version=__version__, uptime_seconds=uptime_seconds), 200
        
    def run():
        app.run(host=host, port=port)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
