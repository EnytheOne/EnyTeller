import sys
import argparse
import subprocess
from .health import emit_positive_health

parser = argparse.ArgumentParser()

parser.add_argument('filename', help='The main script file.')
parser.add_argument('--host', help='Defaults to "0.0.0.0"', default='0.0.0.0')
parser.add_argument('--port', help='Defaults to "8000"', type=int, default=8000)
parser.add_argument('--route', help='Defaults to "/"', default='/')

args = parser.parse_args()

def main():
    filename = args.filename
    emit_positive_health(
        args.host, 
        args.port,
        args.route
    ) 
    subprocess.run(['python3', filename])