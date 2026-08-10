# Bank Statement JSON Schema Reference

This file defines the canonical JSON schema for parsed bank statements.

## Root Object

```json
{
  "account_holder": "Jane Doe",
  "account_number": "****1234",
  "bank_name": "First National Bank",
  "statement_period": {
    "from": "2025-01-01",
    "to": "2025-01-31"
  },
  "currency": "USD",
  "opening_balance": 2000.00,
  "closing_balance": 1450.75,
  "total_credits": 3200.00,
  "total_debits": 3749.25,
  "transactions": [],
  "spending_by_category": {
    "groceries": 320.45,
    "dining": 215.00,
    "utilities": 180.00,
    "shopping": 149.99,
    "salary": 3200.00,
    "other": 883.81
  },
  "parsed_at": "2025-08-04T10:00:00Z",
  "source_file": "attachments/statement_jan2025.pdf"
}
```

## Transaction Object

```json
{
  "date": "2025-01-03",
  "description": "WHOLE FOODS MARKET #123",
  "amount": -85.40,
  "running_balance": 1914.60,
  "category": "groceries",
  "reference": "TXN20250103001"
}
```

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| account_holder | string | Name on the account |
| account_number | string | Masked — last 4 digits only (e.g. ****1234) |
| bank_name | string | Name of the issuing bank |
| statement_period.from | string ISO 8601 | First day of the statement period |
| statement_period.to | string ISO 8601 | Last day of the statement period |
| currency | string ISO 4217 | e.g. USD, EUR, GBP |
| opening_balance | number | Balance at start of period |
| closing_balance | number | Balance at end of period |
| total_credits | number | Sum of all positive (incoming) transactions |
| total_debits | number | Sum of all negative (outgoing) transactions (absolute value) |
| transactions | array | Ordered list of transaction objects |
| spending_by_category | object | Map of category to total amount spent (debits only) |
| parsed_at | string ISO 8601 | Timestamp when parsing occurred |
| source_file | string | Workspace-relative path of the source PDF |

## Supported Categories

| Category | Examples |
|----------|---------|
| salary | Payroll deposits, direct deposits from employer |
| groceries | Supermarkets, food stores |
| dining | Restaurants, cafes, food delivery |
| utilities | Electric, gas, water, internet, phone bills |
| shopping | Retail stores, online shopping |
| travel | Airlines, hotels, car rentals, ride-sharing |
| subscription | Netflix, Spotify, SaaS services, gym memberships |
| atm | Cash withdrawals |
| transfer | Bank transfers, wire transfers, P2P payments |
| healthcare | Pharmacies, doctors, insurance |
| education | Tuition, books, online courses |
| entertainment | Movies, concerts, gaming |
| fuel | Gas stations, EV charging |
| other | Anything that does not fit the above |
