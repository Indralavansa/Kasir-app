import csv
import os
from io import StringIO
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MDB_PATH = BASE_DIR / "data" / "dbamiramart_2026February - Copy (2).MDB"
MDB_PATH = Path(os.environ.get("MDB_PATH", str(DEFAULT_MDB_PATH)))

def parse_tuple_line(line):
    """Parse one line dengan tuple data"""
    # Remove trailing comma and semicolon if present
    line = line.rstrip(',;').strip()
    
    # Must start with ( and end with )
    if not line.startswith('(') or not line.endswith(')'):
        return None
    
    # Remove outer parentheses
    line = line[1:-1]
    
    # Parse as CSV
    try:
        reader = csv.reader(StringIO(line))
        values = next(reader)
        return values
    except Exception as e:
        print(f"CSV Error: {e}")
        return None

# Test with actual data
with open(MDB_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Test first 5 data lines
count = 0
for i, line in enumerate(lines):
    if line.strip().startswith('(NULL'):
        result = parse_tuple_line(line)
        if result:
            count += 1
            if count <= 3:
                print(f"Line {i+1}: OK - {len(result)} values")
        else:
            print(f"Line {i+1}: FAILED")
            print(f"  Original: {repr(line[:50])}...{repr(line[-30:])}")
            line_clean = line.rstrip(',;').strip()
            print(f"  After strip: starts={repr(line_clean[:15])} ends={repr(line_clean[-15:])}")
            
        if count >= 5:
            break
