#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_contracts_api():
    """contracts API를 테스트합니다."""
    base_url = "http://localhost:5000"
    
    # Health check
    print("1. Health check 테스트...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Contracts API 테스트
    print("\n2. Contracts API 테스트...")
    try:
        response = requests.get(f"{base_url}/api/contracts/?per_page=5")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Routes 확인
    print("\n3. Routes 확인...")
    try:
        response = requests.get(f"{base_url}/__routes")
        routes = response.json()['routes']
        contracts_routes = [r for r in routes if 'contracts' in r['rule']]
        print(f"   Contracts 관련 라우트:")
        for route in contracts_routes:
            print(f"     {route['rule']} -> {route['endpoint']} ({route['methods']})")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_contracts_api()

