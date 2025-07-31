#!/usr/bin/env python3
import re

# Read the AI response
with open("ai_response_debug.txt", "r", encoding="utf-8") as f:
    response_text = f.read()

# Test the new pattern
file_pattern = re.compile(
    r"//\s*FILEPATH:\s*([^\n]+)\n```\w*\n([\s\S]*?)\n```", re.MULTILINE
)

files_found = []
for match in file_pattern.finditer(response_text):
    filepath = match.group(1).strip()
    filename = filepath.split("/")[-1] if "/" in filepath else filepath
    files_found.append(filename)
    print(f"Found file: {filename}")

print(f"\nTotal files found: {len(files_found)}")
print(f"Expected: 4 files (types.ts, query.ts, component.tsx, page.tsx)")

if len(files_found) == 4:
    print("✅ Parsing pattern works correctly!")
else:
    print("❌ Parsing pattern needs adjustment")
