#!/bin/bash

# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "email=testuser1@ismart.com&password=Test@123456" | jq -r '.access_token')

echo "=== Token ==="
echo "$TOKEN"

echo -e "\n=== Notificações ==="
curl -s -X GET "http://localhost:8000/api/notifications/" \
    -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n=== Notificações Preferências ==="
curl -s -X GET "http://localhost:8000/api/notifications/preferences" \
    -H "Authorization: Bearer $TOKEN" | jq .

echo -e "\n=== Mentorship Request ==="
curl -s -X POST "http://localhost:8000/api/mentorship/request-mentor" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"reason":"Quero aprender"}' | jq .
