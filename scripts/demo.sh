#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "# Health"
curl -s "$BASE_URL/health"

echo
echo "# Query"
TRACE_ID=$(
  curl -s -X POST "$BASE_URL/query" \
    -H "Content-Type: application/json" \
    -d '{"question":"How do I declare a FastAPI path parameter?"}' \
    | python -c "import json,sys; print(json.load(sys.stdin)['trace_id'])"
)
echo "Trace: $TRACE_ID"

echo
echo "# Streaming query"
curl -N -X POST "$BASE_URL/query" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"question":"How does FastAPI parse request bodies?"}'

echo
echo "# Ingest URL"
curl -s -X POST "$BASE_URL/ingest" \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://fastapi.tiangolo.com/tutorial/"]}'

echo
echo "# Documents"
curl -s "$BASE_URL/documents?limit=5&offset=0"

echo
echo "# Feedback"
curl -s -o /dev/null -w "%{http_code}\n" -X POST "$BASE_URL/feedback" \
  -H "Content-Type: application/json" \
  -d "{\"trace_id\":\"$TRACE_ID\",\"rating\":1}"

echo
echo "# Trace detail"
curl -s "$BASE_URL/traces/$TRACE_ID"

echo
echo "# Recent traces"
curl -s "$BASE_URL/traces?limit=5&offset=0"

echo
echo "# Missing job example"
curl -s "$BASE_URL/ingest/jobs/missing"

