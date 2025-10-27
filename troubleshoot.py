"""
Troubleshooting Tool for Bank Reconciliation System
Helps diagnose common issues with file formats and matching
"""

import pandas as pd
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def print_header():
    """Print diagnostic header"""
    print("\n" + Fore.CYAN + "="*60)
    print(" BANK RECONCILIATION DIAGNOSTIC TOOL")
    print("="*60 + Style.RESET_ALL)

def check_file_exists(filepath):
    """Check if file exists and is readable"""
    if not os.path.exists(filepath):
        print(Fore.RED + f"✗ File not found: {filepath}" + Style.RESET_ALL)
        return False
    
    if not os.access(filepath, os.R_OK):
        print(Fore.RED + f"✗ File not readable: {filepath}" + Style.RESET_ALL)
        return False
    
    print(Fore.GREEN + f"✓ File found: {filepath}" + Style.RESET_ALL)
    return True

def analyze_csv_file(filepath, file_type="Unknown"):
    """Analyze CSV file structure and content"""
    print(f"\n{Fore.YELLOW}Analyzing {file_type} File:{Style.RESET_ALL} {filepath}")
    print("-" * 50)
    
    try:
        # Try to read the file
        df = pd.read_csv(filepath)
        
        print(Fore.GREEN + f"✓ Successfully loaded {len(df)} rows" + Style.RESET_ALL)
        print(f"\n{Fore.CYAN}Column Information:{Style.RESET_ALL}")
        
        # Show column names and types
        for col in df.columns:
            dtype = str(df[col].dtype)
            nulls = df[col].isna().sum()
            print(f"  • {col:30} Type: {dtype:10} Nulls: {nulls}")
        
        # Analyze date columns
        print(f"\n{Fore.CYAN}Date Column Analysis:{Style.RESET_ALL}")
        date_columns = []
        for col in df.columns:
            if any(word in col.lower() for word in ['date', 'posting', 'transaction']):
                date_columns.append(col)
                print(f"  Potential date column: {col}")
                
                # Show sample values
                sample = df[col].head(3).tolist()
                print(f"    Sample values: {sample}")
                
                # Try to parse dates
                try:
                    parsed = pd.to_datetime(df[col])
                    print(Fore.GREEN + f"    ✓ Can parse as dates" + Style.RESET_ALL)
                    print(f"    Date range: {parsed.min()} to {parsed.max()}")
                except:
                    print(Fore.RED + f"    ✗ Cannot parse as dates" + Style.RESET_ALL)
        
        # Analyze amount columns
        print(f"\n{Fore.CYAN}Amount Column Analysis:{Style.RESET_ALL}")
        amount_columns = []
        for col in df.columns:
            if any(word in col.lower() for word in ['amount', 'debit', 'credit', 'withdrawal', 'deposit', 'balance']):
                amount_columns.append(col)
                print(f"  Potential amount column: {col}")
                
                # Show sample values
                sample = df[col].head(5).tolist()
                print(f"    Sample values: {sample}")
                
                # Check for currency symbols
                if df[col].dtype == 'object':
                    has_dollar = df[col].astype(str).str.contains('\\$').any()
                    has_comma = df[col].astype(str).str.contains(',').any()
                    has_parens = df[col].astype(str).str.contains('\\(').any()
                    
                    if has_dollar:
                        print(Fore.YELLOW + f"    ⚠ Contains $ symbols" + Style.RESET_ALL)
                    if has_comma:
                        print(Fore.YELLOW + f"    ⚠ Contains commas" + Style.RESET_ALL)
                    if has_parens:
                        print(Fore.YELLOW + f"    ⚠ Contains parentheses (negative values?)" + Style.RESET_ALL)
                
                # Try to convert to numeric
                try:
                    numeric = pd.to_numeric(df[col].astype(str).str.replace('[$,()]', '', regex=True).str.replace('(', '-'))
                    print(Fore.GREEN + f"    ✓ Can convert to numeric" + Style.RESET_ALL)
                    print(f"    Range: ${numeric.min():,.2f} to ${numeric.max():,.2f}")
                    print(f"    Sum: ${numeric.sum():,.2f}")
                except:
                    print(Fore.RED + f"    ✗ Cannot convert to numeric" + Style.RESET_ALL)
        
        # Check for reference/check number columns
        print(f"\n{Fore.CYAN}Reference Column Analysis:{Style.RESET_ALL}")
        for col in df.columns:
            if any(word in col.lower() for word in ['check', 'ref', 'num', 'number', 'slip']):
                print(f"  Potential reference column: {col}")
                non_null = df[col].notna().sum()
                print(f"    Non-null values: {non_null}/{len(df)}")
                if non_null > 0:
                    sample = df[col].dropna().head(3).tolist()
                    print(f"    Sample values: {sample}")
        
        return df, date_columns, amount_columns
        
    except Exception as e:
        print(Fore.RED + f"✗ Error reading file: {e}" + Style.RESET_ALL)
        return None, [], []

def compare_files(bank_df, qb_df):
    """Compare bank and QuickBooks files for compatibility"""
    print(f"\n{Fore.YELLOW}File Comparison:{Style.RESET_ALL}")
    print("-" * 50)
    
    # Compare date ranges
    try:
        bank_dates = pd.to_datetime(bank_df.iloc[:, 0])  # Assume first column is date
        qb_dates = pd.to_datetime(qb_df['Date'] if 'Date' in qb_df.columns else qb_df.iloc[:, 0])
        
        print(f"\n{Fore.CYAN}Date Range Comparison:{Style.RESET_ALL}")
        print(f"  Bank: {bank_dates.min()} to {bank_dates.max()}")
        print(f"  QuickBooks: {qb_dates.min()} to {qb_dates.max()}")
        
        # Check for overlap
        overlap_start = max(bank_dates.min(), qb_dates.min())
        overlap_end = min(bank_dates.max(), qb_dates.max())
        
        if overlap_start <= overlap_end:
            print(Fore.GREEN + f"  ✓ Date ranges overlap: {overlap_start} to {overlap_end}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"  ✗ No date overlap - files may be from different periods" + Style.RESET_ALL)
            
    except Exception as e:
        print(Fore.RED + f"  ✗ Could not compare dates: {e}" + Style.RESET_ALL)
    
    # Compare transaction counts
    print(f"\n{Fore.CYAN}Transaction Count:{Style.RESET_ALL}")
    print(f"  Bank: {len(bank_df)} transactions")
    print(f"  QuickBooks: {len(qb_df)} transactions")
    diff = abs(len(bank_df) - len(qb_df))
    if diff > 10:
        print(Fore.YELLOW + f"  ⚠ Large difference ({diff} transactions)" + Style.RESET_ALL)

def suggest_mappings(df, file_type="Bank"):
    """Suggest column mappings based on analysis"""
    print(f"\n{Fore.YELLOW}Suggested Mappings for {file_type}:{Style.RESET_ALL}")
    print("-" * 50)
    
    suggestions = {
        'Date': None,
        'Description': None,
        'Amount/Debit': None,
        'Amount/Credit': None,
        'Reference': None,
        'Balance': None
    }
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Date mapping
        if any(word in col_lower for word in ['date', 'posting', 'transaction']) and not suggestions['Date']:
            suggestions['Date'] = col
        
        # Description mapping
        elif any(word in col_lower for word in ['description', 'desc', 'memo', 'details']) and not suggestions['Description']:
            suggestions['Description'] = col
        
        # Amount mappings
        elif 'debit' in col_lower or 'withdrawal' in col_lower:
            suggestions['Amount/Debit'] = col
        elif 'credit' in col_lower or 'deposit' in col_lower:
            suggestions['Amount/Credit'] = col
        elif 'amount' in col_lower and not suggestions['Amount/Debit']:
            suggestions['Amount/Debit'] = col
            suggestions['Amount/Credit'] = col + " (single column)"
        
        # Reference mapping
        elif any(word in col_lower for word in ['check', 'ref', 'num', 'slip']) and not suggestions['Reference']:
            suggestions['Reference'] = col
        
        # Balance mapping
        elif 'balance' in col_lower and not suggestions['Balance']:
            suggestions['Balance'] = col
    
    print(f"\n{Fore.CYAN}Suggested Parser Mappings:{Style.RESET_ALL}")
    for key, value in suggestions.items():
        if value:
            print(f"  {key:15} → {value}")
        else:
            print(f"  {key:15} → " + Fore.RED + "Not found" + Style.RESET_ALL)
    
    return suggestions

def main():
    """Main diagnostic workflow"""
    print_header()
    
    # Default file paths
    bank_file = "data/input/bank_statement.csv"
    qb_file = "data/input/quickbooks_export.csv"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        bank_file = sys.argv[1]
    if len(sys.argv) > 2:
        qb_file = sys.argv[2]
    
    print(f"\n{Fore.CYAN}Files to analyze:{Style.RESET_ALL}")
    print(f"  Bank: {bank_file}")
    print(f"  QuickBooks: {qb_file}")
    
    # Check if files exist
    bank_exists = check_file_exists(bank_file)
    qb_exists = check_file_exists(qb_file)
    
    if not bank_exists and not qb_exists:
        print(f"\n{Fore.RED}No files found to analyze{Style.RESET_ALL}")
        print("\nUsage: python troubleshoot.py [bank_file] [quickbooks_file]")
        return
    
    # Analyze bank file
    bank_df = None
    if bank_exists:
        bank_df, bank_dates, bank_amounts = analyze_csv_file(bank_file, "Bank Statement")
        if bank_df is not None:
            bank_mappings = suggest_mappings(bank_df, "Bank Statement")
    
    # Analyze QuickBooks file
    qb_df = None
    if qb_exists:
        qb_df, qb_dates, qb_amounts = analyze_csv_file(qb_file, "QuickBooks Export")
        if qb_df is not None:
            qb_mappings = suggest_mappings(qb_df, "QuickBooks Export")
    
    # Compare files if both exist
    if bank_df is not None and qb_df is not None:
        compare_files(bank_df, qb_df)
    
    # Provide recommendations
    print(f"\n{Fore.YELLOW}RECOMMENDATIONS:{Style.RESET_ALL}")
    print("=" * 50)
    
    recommendations = []
    
    if bank_df is not None:
        # Check for common issues
        if any('$' in str(val) for val in bank_df.iloc[0].values):
            recommendations.append("Remove currency symbols ($) from amount columns")
        
        if bank_df.isna().any().any():
            recommendations.append("Handle missing/null values in data")
    
    if not recommendations:
        recommendations.append("Files appear to be properly formatted")
        recommendations.append("If matching is not working, check date formats and amount signs")
        recommendations.append("Adjust MATCH_THRESHOLD and DATE_WINDOW in main.py if needed")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print(f"\n{Fore.GREEN}Diagnostic complete!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()