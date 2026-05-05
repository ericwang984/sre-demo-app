#!/bin/bash
# Quick test script to verify all API endpoints

BASE_URL="${1:-http://localhost:8000}"

echo "Testing SRE Demo API Endpoints"
echo "Base URL: $BASE_URL"
echo

# Array of endpoints and expected status codes
declare -A endpoints=(
    ["$BASE_URL/"]=200
    ["$BASE_URL/health"]=200
    ["$BASE_URL/ready"]=200
    ["$BASE_URL/metrics"]=200
    ["$BASE_URL/api/orders"]=200
    ["$BASE_URL/api/orders/1"]=200
    ["$BASE_URL/api/orders/999"]=404
    ["$BASE_URL/api/orders/stats"]=200
    ["$BASE_URL/api/orders?limit=2"]=200
    ["$BASE_URL/api/slow?seconds=1"]=200
    ["$BASE_URL/api/error"]=500
    ["$BASE_URL/api/flaky"]=200
)

passed=0
total=${#endpoints[@]}

for endpoint in "${!endpoints[@]}"; do
    expected=${endpoints[$endpoint]}

    # Make request with timeout
    status=$(curl -s -o /dev/null -w "%{http_code}" -m 30 "$endpoint" 2>/dev/null)

    # For /api/flaky, accept 200 or 500
    if [[ "$endpoint" == *"/api/flaky"* ]]; then
        if [[ "$status" == "200" ]] || [[ "$status" == "500" ]]; then
            echo "✓ PASS - $endpoint (Status: $status, expected 200 or 500)"
            ((passed++))
        else
            echo "✗ FAIL - $endpoint (Status: $status, expected 200 or 500)"
        fi
    else
        if [[ "$status" == "$expected" ]]; then
            echo "✓ PASS - $endpoint (Status: $status)"
            ((passed++))
        else
            echo "✗ FAIL - $endpoint (Status: $status, expected $expected)"
        fi
    fi
done

echo
echo "Results: $passed/$total tests passed"

if [[ $passed -eq $total ]]; then
    echo "All tests passed!"
    exit 0
else
    echo "Some tests failed"
    exit 1
fi
