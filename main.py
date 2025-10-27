"""
Enhanced Bank Reconciliation System - Main Script
With detailed unmatched transaction reporting
"""

import sys
import os
from datetime import datetime
import pandas as pd
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.reconciliation_engine import ReconciliationEngine
from bank_parsers.chase_parser import ChaseParser
from bank_parsers.wells_fargo_parser import WellsFargoParser
# from bank_parsers.bank_of_america_parser import BankOfAmericaParser
from config.settings import *

def print_header():
    """Print colorful header"""
    print("\n" + Fore.CYAN + "="*60)
    print(Fore.CYAN + " ENHANCED BANK RECONCILIATION SYSTEM")
    print(Fore.CYAN + "="*60 + Style.RESET_ALL)

def validate_files(bank_file, qb_file):
    """Validate input files exist"""
    
    if not os.path.exists(bank_file):
        print(Fore.RED + f"✗ Bank file not found: {bank_file}" + Style.RESET_ALL)
        return False
        
    if qb_file and not os.path.exists(qb_file):
        print(Fore.RED + f"✗ QuickBooks file not found: {qb_file}" + Style.RESET_ALL)
        return False
        
    return True

def get_parser(bank_type, file_path):
    """Get appropriate parser based on bank type"""
    parsers = {
        'chase': ChaseParser,
        'wells_fargo': WellsFargoParser,
        # 'bank_of_america': BankOfAmericaParser,
    }
    
    parser_class = parsers.get(bank_type)
    if parser_class:
        return parser_class(file_path)
    else:
        print(Fore.RED + f"✗ Unknown bank type: {bank_type}" + Style.RESET_ALL)
        print(f"  Available banks: {', '.join(parsers.keys())}")
        return None

def print_action_items(engine):
    """Print actionable items based on reconciliation results"""
    print("\n" + Fore.YELLOW + "📋 ACTION ITEMS:" + Style.RESET_ALL)
    
    if len(engine.unmatched_bank) > 0:
        print(f"\n  {Fore.CYAN}1. Review {len(engine.unmatched_bank)} transactions in bank not in books:{Style.RESET_ALL}")
        
        # Group by category
        categories = engine.unmatched_bank.groupby('Category')['Amount'].agg(['count', 'sum'])
        
        for category, row in categories.iterrows():
            print(f"     • {category}: {int(row['count'])} items totaling ${row['sum']:,.2f}")
        
        print("\n     " + Fore.YELLOW + "Actions needed:" + Style.RESET_ALL)
        print("     - Record bank fees in QuickBooks")
        print("     - Enter missing deposits")
        print("     - Investigate any unrecognized transactions")
        
    if len(engine.unmatched_qb) > 0:
        print(f"\n  {Fore.CYAN}2. Review {len(engine.unmatched_qb)} transactions in books not in bank:{Style.RESET_ALL}")
        
        # Check for outstanding checks
        outstanding = engine.reconciliation_summary['Books_Not_Bank'].get('Outstanding_Checks', [])
        if outstanding:
            print(f"     • Outstanding checks: {len(outstanding)} totaling ${sum(c['Amount'] for c in outstanding):,.2f}")
            for check in outstanding[:5]:  # Show first 5
                print(f"       - Check #{check['Check_Number']}: ${check['Amount']:,.2f} ({check['Date']})")
            if len(outstanding) > 5:
                print(f"       ... and {len(outstanding)-5} more")
        
        print("\n     " + Fore.YELLOW + "Actions needed:" + Style.RESET_ALL)
        print("     - Follow up on outstanding checks")
        print("     - Verify deposits in transit")
        print("     - Correct any data entry errors")

def main():
    """
    Main reconciliation workflow
    """
    print_header()
    
    # CONFIGURATION - EDIT THESE FOR YOUR RECONCILIATION
    # ================================================
    BANK_TYPE = "chase"  # Options: "chase", "wells_fargo", "bank_of_america"
    BANK_STATEMENT_FILE = "data/input/bank_statement.csv"
    QUICKBOOKS_FILE = "data/input/quickbooks_export.csv"  # Set to None if not available
    
    # Matching parameters (optional - uses defaults if not specified)
    MATCH_THRESHOLD = DEFAULT_MATCH_THRESHOLD  # Allow $0.01 difference
    DATE_WINDOW = DEFAULT_DATE_WINDOW  # Allow 3-day difference for matching
    
    print(f"\n{Fore.GREEN}Configuration:{Style.RESET_ALL}")
    print(f"  Bank Type: {BANK_TYPE}")
    print(f"  Bank File: {BANK_STATEMENT_FILE}")
    print(f"  QuickBooks File: {QUICKBOOKS_FILE if QUICKBOOKS_FILE else 'Not provided'}")
    print(f"  Match Threshold: ${MATCH_THRESHOLD}")
    print(f"  Date Window: {DATE_WINDOW} days")
    
    # Ensure directories exist
    os.makedirs(INPUT_DIRECTORY, exist_ok=True)
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    os.makedirs(TEMPLATE_DIRECTORY, exist_ok=True)
    
    # Validate files
    if not validate_files(BANK_STATEMENT_FILE, QUICKBOOKS_FILE):
        print(f"\n{Fore.RED}Please ensure input files are in the '{INPUT_DIRECTORY}' folder{Style.RESET_ALL}")
        return
    
    # Get appropriate parser
    parser = get_parser(BANK_TYPE, BANK_STATEMENT_FILE)
    if not parser:
        return
    
    # Create reconciliation engine
    engine = ReconciliationEngine(parser, QUICKBOOKS_FILE)
    
    # Load data
    try:
        engine.load_data()
    except Exception as e:
        print(Fore.RED + f"\n✗ Error loading data: {e}" + Style.RESET_ALL)
        return
    
    # Validate bank data
    issues = parser.validate_data()
    if issues:
        print("\n" + Fore.YELLOW + "⚠ Data validation issues found:" + Style.RESET_ALL)
        for issue in issues:
            print(f"  - {issue}")
    
    # Perform reconciliation if QuickBooks data is available
    if QUICKBOOKS_FILE:
        report_path = engine.reconcile(
            match_threshold=MATCH_THRESHOLD,
            date_window_days=DATE_WINDOW
        )
        
        if report_path:
            print("\n" + Fore.GREEN + "="*60)
            print(" RECONCILIATION COMPLETE")
            print("="*60 + Style.RESET_ALL)
            
            print(f"\n📊 {Fore.GREEN}Full report saved:{Style.RESET_ALL} {report_path}")
            
            print(f"\n{Fore.CYAN}Report Contents:{Style.RESET_ALL}")
            print("  ✓ Executive Summary - High-level overview")
            print("  ✓ Bank Not Books Detail - Line items in bank but not in books")
            print("  ✓ Bank Not Books Summary - Categorized summary")
            print("  ✓ Books Not Bank Detail - Line items in books but not in bank")
            print("  ✓ Books Not Bank Summary - Categorized summary")
            print("  ✓ Outstanding Checks - Checks not yet cleared")
            print("  ✓ QB Import Ready - Ready to import to QuickBooks")
            
            # Print action items
            print_action_items(engine)
    else:
        # Just show bank transactions if no QuickBooks file
        print(f"\n{Fore.YELLOW}No QuickBooks file provided - showing bank transactions only{Style.RESET_ALL}")
        
        # Save bank transactions in QuickBooks format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{OUTPUT_DIRECTORY}/bank_transactions_{BANK_TYPE}_{timestamp}.csv"
        
        qb_format = pd.DataFrame({
            'Date': engine.bank_data['Date'].dt.strftime('%m/%d/%Y'),
            'Description': engine.bank_data['Description'],
            'Reference': engine.bank_data.get('Reference', ''),
            'Debit': engine.bank_data['Debit'].round(2),
            'Credit': engine.bank_data['Credit'].round(2)
        })
        
        qb_format.to_csv(output_file, index=False)
        print(f"\n✓ Bank transactions saved in QuickBooks format: {output_file}")
        print(f"  Total transactions: {len(qb_format)}")
        print(f"  Total debits: ${qb_format['Debit'].sum():,.2f}")
        print(f"  Total credits: ${qb_format['Credit'].sum():,.2f}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Reconciliation cancelled by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()