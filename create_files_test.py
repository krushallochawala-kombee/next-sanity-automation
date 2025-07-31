#!/usr/bin/env python3
import re
from pathlib import Path


def parse_and_create_files(response_text, component_name, component_dir, page_dir):
    """Test function to create files from AI response"""
    print(f"Creating files for '{component_name}'")
    component_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)

    file_pattern = re.compile(
        r"//\s*FILEPATH:\s*([^\n]+)\n```\w*\n([\s\S]*?)\n```", re.MULTILINE
    )

    files_created = {}
    for match in file_pattern.finditer(response_text):
        filepath = match.group(1).strip()
        content = match.group(2).strip()

        # Extract just the filename from the full path
        filename = filepath.split("/")[-1] if "/" in filepath else filepath

        if filename == "page.tsx":
            file_path = page_dir / filename
        else:
            file_path = component_dir / filename

        file_path.write_text(content, encoding="utf-8")
        files_created[filename] = file_path
        print(f"✅ Created file: {file_path}")

    if len(files_created) < 4:
        print(f"❌ Expected 4 code blocks, but only found {len(files_created)}.")
    else:
        print(f"✅ Successfully created all {len(files_created)} files!")

    return files_created


# Read the AI response
with open("ai_response_debug.txt", "r", encoding="utf-8") as f:
    response_text = f.read()

# Test creating files
component_name = "Desktop"
component_dir = Path(f"src/components/generated/{component_name}")
page_dir = Path(f"src/app/desktop/[slug]")

files_created = parse_and_create_files(
    response_text, component_name, component_dir, page_dir
)
print(f"\nFiles created: {list(files_created.keys())}")
