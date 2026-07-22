#!/usr/bin/env python3
import argparse
import json
import logging
import random
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Configuration and Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ChaosMock")

BANNER = r"""
==================================================
                 C H A O S M O C K
         [ Lightweight API Mock & Chaos Engine ]
              coded by asmith762mm-coder
==================================================
"""

class ChaosMockHandler(BaseHTTPRequestHandler):
    routes_config = {}

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_PUT(self):
        self.handle_request("PUT")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def handle_request(self, method):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        logger.info(f"Incoming {method} request for {path}")

        route_def = self.match_route(method, path)
        if not route_def:
            self.send_error_response(404, {"error": "Route not found", "path": path})
            return

        # Chaos Injection: Latency
        latency = route_def.get("latency", 0)
        if latency > 0:
            logger.info(f"Injecting latency: sleeping for {latency} seconds")
            time.sleep(latency)

        # Chaos Injection: Error Rate / Status Code Flaking
        status_code = route_def.get("status", 200)
        error_rate = route_def.get("error_rate", 0.0)
        if error_rate > 0 and random.random() < error_rate:
            status_code = route_def.get("error_status", 500)
            logger.warning(f"Chaos injection triggered: Returning error status {status_code}")

        # Send Response
        response_body = route_def.get("response", {})
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response_body).encode("utf-8"))

    def match_route(self, method, path):
        for route in self.routes_config.get("routes", []):
            if route.get("method", "GET").upper() == method and route.get("path") == path:
                return route
        return None

    def send_error_response(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress default HTTP server stderr logging in favor of our custom logger
        return


def load_config(config_path):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file '{config_path}' not found.")
        return {"routes": []}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON configuration: {e}")
        return {"routes": []}


def run_server(port=5000, config_file="mock_routes.json"):
    print(BANNER)
    ChaosMockHandler.routes_config = load_config(config_file)
    
    server_address = ("", port)
    httpd = HTTPServer(server_address, ChaosMockHandler)
    logger.info(f"ChaosMock server started on port {port}, using config: {config_file}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server gracefully...")
        httpd.server_close()


def main():
    parser = argparse.ArgumentParser(
        description="ChaosMock: A Python mock API server with latency, chaos injection, and request logging."
    )
    parser.add_argument(
        "-p", "--port", type=int, default=5000,
        help="Port to run the mock server on (default: 5000)"
    )
    parser.add_argument(
        "-c", "--config", type=str, default="mock_routes.json",
        help="Path to route mapping JSON file (default: mock_routes.json)"
    )
    
    args = parser.parse_args()
    run_server(port=args.port, config_file=args.config)


if __name__ == "__main__":
    main()
