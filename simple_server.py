#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask server...")
    print("Server will be available at: http://127.0.0.1:5001")
    app.run(debug=True, host='127.0.0.1', port=5001, use_reloader=False)
