#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Available routes:")
    for rule in app.url_map.iter_rules():
        if 'contracts' in rule.rule:
            print(f"  {rule.rule} -> {rule.endpoint} ({rule.methods})")
    
    print("\nStarting server on http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)

