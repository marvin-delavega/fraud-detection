#!/usr/bin/env python
"""
Performance test script for event insertion.
Run this after starting the server to measure insert latency.
"""
import os
import time
import uuid
from decimal import Decimal
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_health():
    """Test health endpoint."""
    with httpx.Client(timeout=30.0) as client:
        response = client.get(f"{BASE_URL}/health/")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200

def test_payment_insert(iterations=10):
    """Test payment insertion latency."""
    merchant_id = uuid.uuid4()
    
    payload = {
        "amount": "100.50",
        "currency": "USD",
        "card_number": "4111111111111111",
        "merchant_id": str(merchant_id)
    }
    
    latencies = []
    
    with httpx.Client(timeout=30.0) as client:
        # Warm-up request
        print("Warming up...")
        client.post(f"{BASE_URL}/payments/", json=payload)
        
        print(f"\nRunning {iterations} payment insertions...")
        for i in range(iterations):
            start = time.perf_counter()
            response = client.post(f"{BASE_URL}/payments/", json=payload)
            elapsed = time.perf_counter() - start
            
            if response.status_code == 200:
                latencies.append(elapsed * 1000)  # Convert to ms
                print(f"  Request {i+1}: {elapsed*1000:.2f}ms - OK")
            else:
                print(f"  Request {i+1}: {elapsed*1000:.2f}ms - ERROR: {response.text}")
    
    if latencies:
        avg = sum(latencies) / len(latencies)
        p50 = sorted(latencies)[len(latencies)//2]
        p95 = sorted(latencies)[int(len(latencies)*0.95)]
        p99 = sorted(latencies)[int(len(latencies)*0.99)]
        
        print(f"\n--- Latency Statistics (ms) ---")
        print(f"  Average: {avg:.2f}")
        print(f"  P50:     {p50:.2f}")
        print(f"  P95:     {p95:.2f}")
        print(f"  P99:     {p99:.2f}")
        print(f"  Min:     {min(latencies):.2f}")
        print(f"  Max:     {max(latencies):.2f}")

if __name__ == "__main__":
    print(f"Testing against: {BASE_URL}")
    
    if test_health():
        test_payment_insert(10)
    else:
        print("Health check failed, skipping payment test")