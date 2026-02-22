import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MDB_PATH = BASE_DIR / "data" / "dbamiramart_2026February - Copy (2).MDB"
MDB_PATH = Path(os.environ.get("MDB_PATH", str(DEFAULT_MDB_PATH)))

with open(MDB_PATH, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Count lines that look like data lines
data_lines = []
for i, line in enumerate(lines):
    if line.strip().startswith('(NULL'):
        # Check if line ends with ), or );
        if line.rstrip().endswith('),') or line.rstrip().endswith(');'):
            data_lines.append((i, 'complete'))
        else:
            data_lines.append((i, 'incomplete'))

print(f'Complete data lines: {sum(1 for _, t in data_lines if t == "complete")}')
print(f'Incomplete data lines: {sum(1 for _, t in data_lines if t == "incomplete")}')
print(f'Total data lines: {len(data_lines)}')

# Show first few
print('\nFirst 10 data lines:')
for line_num, typ in data_lines[:10]:
    line = lines[line_num]
    print(f'  Line {line_num+1}: {typ:10} - ends: {repr(line.rstrip()[-20:])}')
