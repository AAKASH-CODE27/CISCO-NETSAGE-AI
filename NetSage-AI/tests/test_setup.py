import os
import sys
import csv

# Add project root to sys.path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    try:
        from rule_checker import checker
        from ai import diagnosis
        print("PASS: Modules imported successfully.")
    except ImportError as e:
        print(f"FAIL: Module import error: {e}")
        sys.exit(1)

def test_directories():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    dirs_to_check = [
        'data', 'prompts', 'rule_checker', 'ai', 'review',
        'dashboard', 'packet_tracer', 'docs', 'demo', 'tests'
    ]
    all_exist = True
    for d in dirs_to_check:
        if not os.path.isdir(os.path.join(base_dir, d)):
            print(f"FAIL: Directory {d} does not exist.")
            all_exist = False
    
    if all_exist:
        print("PASS: All required directories exist.")
    else:
        sys.exit(1)

def test_csv_schemas():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    cases_csv = os.path.join(base_dir, 'data', 'cases.csv')
    human_review_csv = os.path.join(base_dir, 'review', 'human_review.csv')
    
    cases_header_expected = ["case_id", "symptom", "topology_note", "show_outputs", "expected_fault", "osi_layer", "concept", "severity"]
    human_review_header_expected = ["case_id", "ai_root_cause", "ai_confidence", "human_decision", "human_correction", "reason", "reviewer", "review_timestamp"]
    
    all_pass = True
    
    with open(cases_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != cases_header_expected:
            print(f"FAIL: cases.csv header mismatch.\nExpected: {cases_header_expected}\nGot: {header}")
            all_pass = False
            
    with open(human_review_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        if header != human_review_header_expected:
            print(f"FAIL: human_review.csv header mismatch.\nExpected: {human_review_header_expected}\nGot: {header}")
            all_pass = False

    if all_pass:
        print("PASS: CSV schemas validated successfully.")
    else:
        sys.exit(1)

def test_dataset_validation():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cases_csv = os.path.join(base_dir, 'data', 'cases.csv')
    
    if not os.path.exists(cases_csv):
        print("FAIL: cases.csv does not exist.")
        sys.exit(1)
        
    with open(cases_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    if len(rows) != 30:
        print(f"FAIL: Expected exactly 30 cases, found {len(rows)}.")
        sys.exit(1)
        
    case_ids = [r['case_id'] for r in rows]
    if len(set(case_ids)) != len(case_ids):
        print("FAIL: Case IDs are not unique.")
        sys.exit(1)
        
    required_columns = ["case_id", "symptom", "topology_note", "show_outputs", "expected_fault", "osi_layer", "concept", "severity"]
    for col in required_columns:
        if col not in rows[0].keys():
            print(f"FAIL: Required column {col} is missing.")
            sys.exit(1)
            
    for i, row in enumerate(rows):
        for col in required_columns:
            if not row[col].strip():
                print(f"FAIL: Row {i+1} has empty required field: {col}")
                sys.exit(1)
                
    categories = {"VLAN": 0, "Gateway": 0, "DHCP": 0, "DNS": 0, "Routing": 0, "ACL": 0, "NAT": 0, "Wireless": 0, "Interface/connectivity": 0}
    for row in rows:
        concept = row['concept']
        if concept in categories:
            categories[concept] += 1
        else:
            print(f"FAIL: Unknown concept '{concept}' found.")
            sys.exit(1)
            
    expected_categories = {"VLAN": 4, "Gateway": 2, "DHCP": 4, "DNS": 3, "Routing": 5, "ACL": 4, "NAT": 3, "Wireless": 2, "Interface/connectivity": 3}
    for cat, count in expected_categories.items():
        if categories[cat] != count:
            print(f"FAIL: Category {cat} expected {count} cases, found {categories[cat]}.")
            sys.exit(1)
            
    valid_severities = {"Low", "Medium", "High", "Critical"}
    for row in rows:
        if row['severity'] not in valid_severities:
            print(f"FAIL: Invalid severity '{row['severity']}' found.")
            sys.exit(1)
            
    print("PASS: Dataset validation completed successfully.")

if __name__ == "__main__":
    print("Running basic tests...")
    test_directories()
    test_imports()
    test_csv_schemas()
    test_dataset_validation()
    print("ALL TESTS PASSED.")
