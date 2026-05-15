# Acme Payments Error Handling

Acme Payments returns structured errors so client applications can distinguish validation mistakes from temporary service failures.

## Error response shape

Every error response includes a machine-readable `code`, a human-readable `message`, and a `request_id` for support.

```json
{
  "code": "card_declined",
  "message": "The card was declined.",
  "request_id": "req_123"
}
```

## Retryable errors

Retry only requests that fail with `rate_limited`, `service_unavailable`, or `gateway_timeout`. Use exponential backoff and preserve idempotency keys for write operations.

## Non-retryable errors

Do not retry validation errors such as `missing_email`, `invalid_currency`, or `card_declined`. Show the message to the user and ask them to correct the input.

