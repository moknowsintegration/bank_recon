# Quick Guide: Adding a New Bank Parser

## Step 1: Analyze Your Bank's CSV Format

Run the diagnostic tool on your bank's CSV:
```bash
python troubleshoot.py path/to/your/bank.csv
```

Note the column names for:
- Date
- Description
- Amount (or Debit/Credit)
- Reference/Check Number
- Balance

## Step 2: Copy Parser Template

Copy `bank_parsers/wells_fargo_parser.py` and rename it:
```
bank_parsers/your_bank_parser.py
```

## Step 3: Update Parser Class

```python
class YourBankParser(BaseBankParser):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.bank_name = "Your Bank Name"  # <-- Change this
```

## Step 4: Map Your Columns

### Example Column Mappings:

**Bank of America:**
```python
self.parsed_data['Date'] = self.raw_data['Date'].apply(self.extract_date)
self.parsed_data['Description'] = self.raw_data['Description']
self.parsed_data['Debit'] = self.raw_data['Amount'].apply(
    lambda x: abs(x) if x < 0 else 0
)
self.parsed_data['Credit'] = self.raw_data['Amount'].apply(
    lambda x: x if x > 0 else 0
)
```

**Wells Fargo:**
```python
self.parsed_data['Date'] = self.raw_data['Date'].apply(self.extract_date)
self.parsed_data['Description'] = self.raw_data['Description']
self.parsed_data['Debit'] = self.raw_data['Withdrawals'].fillna(0)
self.parsed_data['Credit'] = self.raw_data['Deposits'].fillna(0)
```

**TD Bank:**
```python
self.parsed_data['Date'] = self.raw_data['DATE'].apply(self.extract_date)
self.parsed_data['Description'] = self.raw_data['DESCRIPTION']
self.parsed_data['Debit'] = self.raw_data['DEBIT'].fillna(0)
self.parsed_data['Credit'] = self.raw_data['CREDIT'].fillna(0)
```

## Step 5: Update Date Parsing

Common date formats:
```python
def extract_date(self, date_string):
    # MM/DD/YYYY (Most US banks)
    return pd.to_datetime(date_string, format='%m/%d/%Y')
    
    # YYYY-MM-DD (International)
    return pd.to_datetime(date_string, format='%Y-%m-%d')
    
    # DD/MM/YYYY (European)
    return pd.to_datetime(date_string, format='%d/%m/%Y')
    
    # MM-DD-YYYY (Alternative US)
    return pd.to_datetime(date_string, format='%m-%d-%Y')
```

## Step 6: Update Amount Parsing

Handle different formats:
```python
def extract_amount(self, amount_string):
    if pd.isna(amount_string):
        return 0.0
    
    amount = str(amount_string)
    
    # Remove currency symbols
    amount = amount.replace('$', '').replace('£', '').replace('€', '')
    
    # Remove thousands separators
    amount = amount.replace(',', '')
    
    # Handle parentheses (negative)
    if '(' in amount and ')' in amount:
        amount = amount.replace('(', '-').replace(')', '')
    
    # Handle CR/DR notation
    if 'CR' in amount:
        amount = amount.replace('CR', '')
    if 'DR' in amount:
        amount = '-' + amount.replace('DR', '')
    
    return float(amount)
```

## Step 7: Register Parser

Add to `main.py`:
```python
from bank_parsers.your_bank_parser import YourBankParser

def get_parser(bank_type, file_path):
    parsers = {
        'chase': ChaseParser,
        'wells_fargo': WellsFargoParser,
        'your_bank': YourBankParser,  # <-- Add this
    }
```

## Step 8: Test Your Parser

1. Place sample bank file in `data/input/`
2. Update `main.py`:
   ```python
   BANK_TYPE = "your_bank"
   BANK_STATEMENT_FILE = "data/input/your_bank.csv"
   ```
3. Run: `python main.py`

## Common Column Names by Bank

| Bank | Date Column | Description | Debit | Credit | Balance |
|------|------------|-------------|-------|--------|---------|
| Chase | Posting Date | Description | Amount (<0) | Amount (>0) | Balance |
| Wells Fargo | Date | Description | Withdrawals | Deposits | Balance |
| Bank of America | Date | Description | Amount (<0) | Amount (>0) | Running Bal. |
| TD Bank | DATE | DESCRIPTION | DEBIT | CREDIT | BALANCE |
| Citi | Date | Description | Debit | Credit | Balance |
| PNC | Date | Description | Withdrawals | Deposits | Balance |
| US Bank | Date | Description | Amount | - | Balance |
| Capital One | Transaction Date | Description | Debit | Credit | Balance |

## Troubleshooting

If your parser isn't working:

1. **Check column names**: Print `self.raw_data.columns` in `load_statement()`
2. **Check date format**: Print sample dates to see format
3. **Check amount signs**: Verify if debits are negative or positive
4. **Run diagnostic**: `python troubleshoot.py your_bank_file.csv`

## Need Help?

Run the diagnostic tool:
```bash
python troubleshoot.py data/input/your_bank.csv
```

This will show you:
- Exact column names
- Date formats
- Amount formats
- Suggested mappings