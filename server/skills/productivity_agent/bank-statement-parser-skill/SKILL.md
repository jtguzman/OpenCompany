---
name: bank-statement-parser-skill
description: Parse bank statements from PDF or email attachments. Extracts transactions, balances, account info, and produces structured summaries. Supports multi-page PDFs, CSV export, and spending analysis.
allowed-tools: "documentParser,msMail,fileModify,pythonExecutor,javascriptExecutor"
metadata:
  author: opencompany
  version: "1.0"
  category: productivity

---

# Bank Statement Parser Skill

Parse bank statements from PDF files or email attachments. Extract transactions, balances, and account metadata, then produce structured JSON, CSV, or Markdown summaries with optional spending analysis.

## Overview

This skill orchestrates three stages:

1. **Acquire** – get the PDF from a workspace path, a URL, or an Outlook email attachment.
2. **Extract** – run the Document Parser to convert the PDF to raw text.
3. **Structure** – use a Python/JS executor or LLM reasoning to parse the raw text into a typed transaction list, then optionally export to CSV or analyse spending by category.

---

## Stage 1 — Acquire the Statement

### Option A: File already in workspace
If the user provides a path (e.g. `statements/jan2025.pdf`), skip to Stage 2.

### Option B: Download from Outlook email attachment

1. Search for the email:
```json
{
  "operation": "search",
  "query": "bank statement",
  "search_max_results": 10
}
```

2. List attachments on the matching message:
```json
{
  "operation": "list_attachments",
  "message_id": "<message_id from search>"
}
```

3. Download the PDF attachment to the workspace:
```json
{
  "operation": "download_attachments",
  "message_id": "<message_id>",
  "attachment_id": "<attachment_id>"
}
```
The tool returns the workspace path (e.g. `attachments/statement.pdf`). Use that path in Stage 2.

---

## Stage 2 — Extract Text with Document Parser

Pass the workspace-relative path to the Document Parser tool:

```json
{
  "file_path": "attachments/statement.pdf",
  "parser": "pypdf"
}
```

Use `parser: "marker"` for scanned/image-based PDFs (requires GPU). Use `parser: "unstructured"` for mixed-format statements.

The tool returns raw extracted text. Pass this to Stage 3.

---

## Stage 3 — Parse & Structure Transactions

### 3a. LLM Extraction (default)

Ask the LLM to extract a structured list from the raw text. Use this prompt template:

```
You are a bank statement parser. Given the following raw text extracted from a bank statement PDF, extract:

1. Account holder name
2. Account number (mask all but last 4 digits)
3. Statement period (start date, end date)
4. Opening balance
5. Closing balance
6. A list of transactions, each with:
   - date (ISO 8601: YYYY-MM-DD)
   - description
   - amount (positive = credit, negative = debit)
   - running_balance (if present)
   - category (infer from description: e.g. groceries, utilities, salary, transfer, ATM, dining, travel, subscription, other)

Return valid JSON only, matching this schema:
{
  "account_holder": "string",
  "account_number": "****XXXX",
  "statement_period": { "from": "YYYY-MM-DD", "to": "YYYY-MM-DD" },
  "opening_balance": 0.00,
  "closing_balance": 0.00,
  "currency": "USD",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "string",
      "amount": 0.00,
      "running_balance": 0.00,
      "category": "string"
    }
  ]
}

RAW TEXT:
<insert extracted text here>
```

### 3b. Spending Analysis (optional)

After extracting transactions, compute a category breakdown:

```python
from collections import defaultdict

def analyse_spending(transactions):
    totals = defaultdict(float)
    for t in transactions:
        if t["amount"] < 0:                       # debits only
            totals[t["category"]] += abs(t["amount"])
    return dict(sorted(totals.items(), key=lambda x: -x[1]))
```

### 3c. Export to CSV (optional)

Write the transaction list to a CSV file in the workspace:

```json
{
  "operation": "write",
  "file_path": "output/statement_<YYYY-MM>.csv",
  "content": "date,description,amount,running_balance,category\n2025-01-03,AMAZON,-49.99,1950.01,shopping\n..."
}
```

---

## Common Workflows

### 1. Parse a PDF already in the workspace
```
1. documentParser({ file_path: "statements/jan2025.pdf", parser: "pypdf" })
2. LLM extraction prompt → structured JSON
3. (Optional) Write CSV with fileModify
4. (Optional) Summarise spending by category
```

### 2. Parse latest bank statement from email
```
1. ms_mail({ operation: "search", query: "bank statement" })
2. ms_mail({ operation: "list_attachments", message_id: "..." })
3. ms_mail({ operation: "download_attachments", message_id: "...", attachment_id: "..." })
4. documentParser({ file_path: "<returned path>", parser: "pypdf" })
5. LLM extraction → structured JSON
```

### 3. Monthly spending report
```
1. Acquire + parse statement (workflows 1 or 2 above)
2. Run spending analysis
3. Format as Markdown table and reply to user
```

---

## Output Format

Always return results in this structure when reporting to the user:

```
## Bank Statement Summary
**Account:** **** **** **** 1234
**Period:** Jan 1 – Jan 31, 2025
**Opening Balance:** $2,000.00
**Closing Balance:** $1,450.75

### Transactions (32 total)
| Date       | Description         | Amount    | Category    |
|------------|---------------------|-----------|-------------|
| 2025-01-03 | AMAZON              | -$49.99   | shopping    |
| 2025-01-05 | SALARY DEPOSIT      | +$3,200.00| salary      |
| ...        | ...                 | ...       | ...         |

### Spending by Category
| Category    | Total Spent |
|-------------|-------------|
| groceries   | $320.45     |
| dining      | $215.00     |
| utilities   | $180.00     |
| ...         | ...         |
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| PDF is scanned/image-only | Retry with `parser: "marker"` |
| No attachment found in email | Ask user to forward or upload the PDF manually |
| Parsing returns garbled text | Try `parser: "unstructured"` as fallback |
| Transactions don't sum to closing balance | Flag discrepancy in the summary |
| Multi-account statement | Split into separate transaction lists per account section |

---

## Tips

- **Always mask account numbers** — show only the last 4 digits in any output.
- For **multi-page statements**, the Document Parser handles pagination automatically; pass the full `file_path` once.
- If the user asks for a **specific month**, filter transactions by date after extraction.
- For **foreign currency** transactions, preserve the original currency code alongside the converted amount if both appear in the statement.
- Infer **categories** conservatively; prefer `other` over a wrong category.
