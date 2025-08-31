#!/usr/bin/env python3
"""
Simple HTTP Server Mock for Chatter Frontend Testing

This provides basic API endpoints using Python's built-in http.server
to demonstrate that the frontend functionality is working.
"""

import json
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


class ChatterMockHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')

    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path

        if path == '/health':
            self.send_json_response({
                "status": "healthy",
                "version": "0.1.0-mock",
                "timestamp": datetime.now().isoformat()
            })
        elif path == '/api/v1/health':
            self.send_json_response({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "database": "mock",
                    "cache": "mock",
                    "llm": "mock"
                }
            })
        elif path == '/api/v1/conversations':
            self.send_json_response({
                "conversations": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            })
        elif path == '/api/v1/agents':
            self.send_json_response({
                "agents": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            })
        elif path == '/api/v1/documents':
            self.send_json_response({
                "documents": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            })
        elif path == '/api/v1/profiles':
            self.send_json_response({
                "profiles": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            })
        elif path == '/api/v1/prompts':
            self.send_json_response({
                "prompts": [],
                "total": 0,
                "page": 1,
                "per_page": 20
            })
        elif path == '/api/v1/auth/me':
            # Check for Authorization header
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self.send_json_response({"detail": "Not authenticated"}, 401)
                return

            self.send_json_response({
                "id": "1",
                "username": "admin",
                "email": "admin@chatter.com",
                "full_name": "Administrator",
                "role": "admin",
                "is_active": True,
                "created_at": datetime.now().isoformat()
            })
        else:
            self.send_json_response({"detail": "Not found"}, 404)

    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path

        if path == '/api/v1/auth/login':
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body.decode())
                    username = data.get('username')
                    password = data.get('password')

                    # Simple auth check
                    if username == 'admin' and password == 'admin':
                        token = str(uuid.uuid4())
                        self.send_json_response({
                            "access_token": token,
                            "token_type": "bearer",
                            "user": {
                                "id": "1",
                                "username": "admin",
                                "email": "admin@chatter.com",
                                "full_name": "Administrator",
                                "role": "admin",
                                "is_active": True,
                                "created_at": datetime.now().isoformat()
                            },
                            "expires_in": 3600
                        })
                        return
                    else:
                        self.send_json_response({"detail": "Invalid credentials"}, 401)
                        return
                except json.JSONDecodeError:
                    self.send_json_response({"detail": "Invalid JSON"}, 400)
                    return

            self.send_json_response({"detail": "Missing request body"}, 400)
        else:
            self.send_json_response({"detail": "Not found"}, 404)

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_server():
    """Run the mock server"""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, ChatterMockHandler)

    print("🚀 Chatter Mock Backend starting...")
    print("📍 Available at: http://localhost:8000")
    print("🔑 Login with: admin/admin")
    print("🔄 CORS enabled for http://localhost:3000")
    print("📡 Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
