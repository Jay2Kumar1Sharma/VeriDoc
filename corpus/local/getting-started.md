# Acme Payments Getting Started

Acme Payments is a fictional API used by VeriDoc's local corpus. It exposes a small set of HTTP endpoints for creating customers, attaching payment methods, and charging invoices.

## Authentication

Every request requires an API key in the `Authorization` header.

```bash
curl https://api.acme-payments.test/v1/customers \
  -H "Authorization: Bearer acme_test_key"
```

## Create a customer

Send a JSON body with an email address and optional metadata. The API returns a stable customer identifier that starts with `cus_`.

```json
{
  "email": "team@example.com",
  "metadata": {
    "plan": "starter"
  }
}
```

## Sandbox mode

Sandbox mode never moves real money. Use it for demos, integration tests, and local development.

