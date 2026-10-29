#!/bin/bash
set -e
cd /mnt/c/Users/Maryeel/Desktop/SystemPr/lab11/sws

echo "=== STARTING SWS WEB SERVER IN BACKGROUND (PORT 8080) ==="
# Kill any existing instances
pkill -9 sws 2>/dev/null || true
sleep 1

# Start sws daemon
./sws -p 8080 -c cgi-bin -l access.log www
sleep 1

echo "--- 1. Testing GET / (Root index.html) ---"
curl -i http://localhost:8080/

echo "--- 2. Testing HEAD / (Headers only) ---"
curl -I http://localhost:8080/

echo "--- 3. Testing GET /test.txt ---"
curl -i http://localhost:8080/test.txt

echo "--- 4. Testing Directory Indexing /docs/ ---"
curl -i http://localhost:8080/docs/

echo "--- 5. Testing CGI Execution /cgi-bin/hello.cgi?user=NguyenHoangLuc&role=TeamLeader ---"
curl -i "http://localhost:8080/cgi-bin/hello.cgi?user=NguyenHoangLuc&role=TeamLeader"

echo "--- 6. Testing 404 Not Found (/nonexistent) ---"
curl -i http://localhost:8080/nonexistent || true

echo "--- 7. Testing 400 Bad Request / Path Traversal (/../../etc/passwd) ---"
curl -i "http://localhost:8080/../../etc/passwd" || true

echo "--- 8. Testing If-Modified-Since (304 Not Modified) ---"
LAST_MOD=$(curl -sI http://localhost:8080/test.txt | grep "Last-Modified:" | cut -d' ' -f2-)
echo "Server Last-Modified: $LAST_MOD"
curl -i -H "If-Modified-Since: $LAST_MOD" http://localhost:8080/test.txt

echo "--- 9. Checking Apache Common Access Log (access.log) ---"
sleep 1
cat access.log

# Cleanup server
pkill -9 sws 2>/dev/null || true
echo "=== ALL SWS TESTS COMPLETED SUCCESSFULLY ==="
