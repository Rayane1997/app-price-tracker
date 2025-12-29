#!/bin/bash
# Phase K: Price History API Endpoints - Test Commands
# Run these commands to verify the endpoints are working

echo "=================================="
echo "Phase K: Price History API Tests"
echo "=================================="
echo ""

echo "1. Testing Price History Endpoint (7 days)"
echo "-------------------------------------------"
curl -s 'http://localhost:8001/api/v1/products/1/price-history?period=7d' | python3 -m json.tool
echo ""

echo "2. Testing Price Statistics Endpoint"
echo "-------------------------------------"
curl -s 'http://localhost:8001/api/v1/products/1/price-history/stats' | python3 -m json.tool
echo ""

echo "3. Testing Chart Data Endpoint (30 days)"
echo "-----------------------------------------"
curl -s 'http://localhost:8001/api/v1/products/1/price-history/chart?period=30d' | python3 -m json.tool
echo ""

echo "4. Testing 404 Error Handling"
echo "------------------------------"
echo "Expected: 404 Not Found"
curl -s -w "\nHTTP Status: %{http_code}\n" 'http://localhost:8001/api/v1/products/99999/price-history' | python3 -m json.tool
echo ""

echo "5. Testing Invalid Parameter Validation"
echo "----------------------------------------"
echo "Expected: 422 Validation Error"
curl -s -w "\nHTTP Status: %{http_code}\n" 'http://localhost:8001/api/v1/products/1/price-history?period=invalid' | python3 -m json.tool
echo ""

echo "=================================="
echo "All Tests Complete!"
echo "=================================="
