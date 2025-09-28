#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app

app = create_app()

with app.app_context():
    print("Testing contracts API...")
    
    # Test 1: Check if routes are registered
    print("\n1. Registered routes:")
    for rule in app.url_map.iter_rules():
        if 'contracts' in rule.rule:
            print(f"   {rule.rule} -> {rule.endpoint} ({rule.methods})")
    
    # Test 2: Try to import the contracts module
    print("\n2. Testing contracts module import:")
    try:
        from routes.contracts import get_contracts
        print("   ✓ get_contracts function imported successfully")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
    
    # Test 3: Test database connection
    print("\n3. Testing database connection:")
    try:
        from models import db, Contract
        print("   ✓ Models imported successfully")
        
        # Try to query the database
        count = Contract.query.count()
        print(f"   ✓ Database query successful, found {count} contracts")
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test the actual function
    print("\n4. Testing get_contracts function:")
    try:
        with app.test_request_context('/api/contracts/?per_page=5'):
            from flask import request
            print(f"   Request URL: {request.url}")
            print(f"   Request args: {dict(request.args)}")
            
            result = get_contracts()
            print(f"   ✓ Function executed successfully: {result}")
    except Exception as e:
        print(f"   ✗ Function execution failed: {e}")
        import traceback
        traceback.print_exc()

