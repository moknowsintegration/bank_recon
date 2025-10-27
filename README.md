# Bank Reconciliation System

## 📋 Overview
Professional bank reconciliation system that automatically matches transactions between bank statements and QuickBooks, identifying discrepancies with detailed line-item reporting.

## ✨ Key Features
- **Multi-bank support** with modular parser system
- **Detailed unmatched transaction reporting** (both directions)
- **Automatic categorization** of transactions
- **Outstanding check identification**
- **QuickBooks/SaasAnt compatible** import formats
- **Executive summary** with actionable insights
- **Color-coded console output** for easy reading

## 🚀 Quick Start

### 1. Setup Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Test Reconciliation
```bash
python main.py
```

## 📁 Project Structure
```
bank_reconciliation/
│
├── core/                      # Core reconciliation logic
│   ├── base_parser.py        # Base parser class
│   └── reconciliation_engine.py  # Main reconciliation engine
│
├── bank_parsers/             # Bank-specific parsers
│   ├── chase_parser.py       # Chase bank parser
│   └── wells_fargo_parser.py # Wells Fargo template
│
├── data/
│   ├── input/               # Place input files here
│   │   ├── bank_statement.csv
│   │   └── quickbooks_export.csv
│   └── output/              # Reports saved here
│
├── config/
│   └── settings.py          # Configuration settings
│
├── main.py                  # Main execution script
├── troubleshoot.py          # Diagnostic tool
└── README.md               # This file
```

## 🏦 Supported Banks

| Bank | Status | Parser File |
|------|--------|------------|
| Chase | ✅ Ready | chase_parser.py |
| Wells Fargo | 🔧 Template | wells_fargo_parser.py |
| Bank of America | 📋 Planned | - |

## 📊 Output Reports

The system generates a comprehensive Excel report with these tabs:

1. **Executive_Summary** - High-level reconciliation overview
2. **Bank_Not_Books_Detail** - Line items in bank but not in QuickBooks
3. **Bank_Not_Books_Summary** - Categorized summary by transaction type
4. **Books_Not_Bank_Detail** - Line items in QuickBooks but not in bank
5. **Books_Not_Bank_Summary** - Categorized summary
6. **Outstanding_Checks** - Checks written but not yet cleared
7. **Matched_Transactions** - Successfully matched items
8. **QB_Import_Ready** - Format ready for QuickBooks import

## 🔧 Configuration

Edit `main.py` to configure:

```python
# Bank and file settings
BANK_TYPE = "chase"
BANK_STATEMENT_FILE = "data/input/bank_statement.csv"
QUICKBOOKS_FILE = "data/input/quickbooks_export.csv"

# Matching parameters
MATCH_THRESHOLD = 0.01  # Allow $0.01 difference
DATE_WINDOW = 3  # Allow 3-day date difference
```

## 📝 Adding a New Bank

### Step 1: Create Parser File
Create `/bank_parsers/your_bank_parser.py`:

```python
from core.base_parser import BaseBankParser

class YourBankParser(BaseBankParser):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.bank_name = "Your Bank"
    
    def load_statement(self):
        # Load CSV file
        pass
    
    def parse_transactions(self):
        # Map columns to standard format
        pass
    
    def extract_date(self, date_string):
        # Parse date format
        pass
    
    def extract_amount(self, amount_string):
        # Parse amount format
        pass
```

### Step 2: Map Columns
Identify your bank's column names and map them:
- Date → `Date`
- Description → `Description`
- Amount/Debit/Credit → `Debit` and `Credit`
- Reference/Check# → `Reference`
- Balance → `Balance`

### Step 3: Update Main Script
Add your parser to `main.py`:

```python
from bank_parsers.your_bank_parser import YourBankParser

# In get_parser function:
'your_bank': YourBankParser,
```

## 🐛 Troubleshooting

### Run Diagnostic Tool
```bash
python troubleshoot.py
```

### Common Issues

#### "No such file or directory"
- Ensure files are in `data/input/` folder
- Check file names match configuration

#### Date parsing errors
- Check date format in your bank's CSV
- Update `extract_date()` method in parser
- Common formats: MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD

#### Amount parsing errors
- Check for currency symbols ($)
- Check decimal separator (. vs ,)
- Check negative number format: -123.45 vs (123.45)

#### No matches found
- Verify date columns are parsing correctly
- Check if amounts need sign reversal
- Adjust `MATCH_THRESHOLD` and `DATE_WINDOW`

#### Decimal/SaasAnt issues
- Ensure all amounts have 2 decimal places
- Remove any formatting (commas, currency symbols)
- Check for trailing zeros

## 📈 Sample Console Output

```
==================================================
 ENHANCED BANK RECONCILIATION SYSTEM
==================================================

Configuration:
  Bank Type: chase
  Bank File: data/input/bank_statement.csv
  QuickBooks File: data/input/quickbooks_export.csv
  Match Threshold: $0.01
  Date Window: 3 days

==================================================
LOADING DATA
==================================================
✓ Bank data loaded: 12 transactions
✓ QuickBooks data loaded: 10 transactions

==================================================
RECONCILIATION PROCESS
==================================================

Matching transactions...

✓ Exact matches: 7
✓ Fuzzy matches: 0
⚠ In Bank, Not in Books: 5
⚠ In Books, Not in Bank: 3

==================================================
RECONCILIATION SUMMARY
==================================================

📘 IN BANK, NOT IN BOOKS:
   Total: 5 transactions
   Debits: $37.00
   Credits: $1,015.25
   Net Impact: $978.25

   By Category:
   - Bank Fees: 2 items, $37.00
   - Interest/Dividends: 1 items, $15.25
   - Transfer: 1 items, $1,000.00

📗 IN BOOKS, NOT IN BANK:
   Total: 3 transactions
   Debits: $450.00
   Credits: $2,500.00
   Net Impact: $2,050.00

   By Category:
   - Check: 1 items, $450.00
   - Deposit: 1 items, $2,500.00

   ⚠ Outstanding Checks: 1 totaling $450.00

✓ Detailed report saved: data/output/reconciliation_detailed_Chase Bank_20251026_153045.xlsx

==================================================
 RECONCILIATION COMPLETE
==================================================

📋 ACTION ITEMS:

  1. Review 5 transactions in bank not in books:
     • Bank Fees: 2 items totaling $37.00
     • Interest/Dividends: 1 items totaling $15.25
     • Transfer: 1 items totaling $1,000.00

     Actions needed:
     - Record bank fees in QuickBooks
     - Enter missing deposits
     - Investigate any unrecognized transactions

  2. Review 3 transactions in books not in bank:
     • Outstanding checks: 1 totaling $450.00
       - Check #1005: $450.00 (10/26/2025)

     Actions needed:
     - Follow up on outstanding checks
     - Verify deposits in transit
     - Correct any data entry errors
```

## 💡 Tips for Best Results

1. **Consistent Date Formats**: Ensure both files use the same date format
2. **Clean Data**: Remove header rows or summary lines from bank exports
3. **Check Numbers**: Include check numbers for easier tracking
4. **Regular Reconciliation**: Run monthly for easier discrepancy resolution
5. **Backup Original Files**: Keep copies of original exports

## 🔐 Security Notes

- Never commit files with real financial data to version control
- Add `data/` to `.gitignore` 
- Use environment variables for sensitive configuration
- Encrypt backup files containing financial information

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Run `python troubleshoot.py` for diagnostics
3. Review parser column mappings
4. Verify CSV file formats

## 📄 License

This software is provided for internal use only. Ensure compliance with your organization's data handling policies.

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Python Required**: 3.7+