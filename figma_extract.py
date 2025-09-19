import os
import json
import requests
from dotenv import load_dotenv

# --- Helper Functions for Node Simplification ---

def is_image_node(node):
    """Checks if a node has an image fill."""
    if 'fills' in node and isinstance(node['fills'], list):
        for fill in node['fills']:
            if fill.get('type') == 'IMAGE':
                return True
    return False

def simplify_node(node):
    """
    Recursively processes a Figma node to extract essential information.
    This creates a clean, semantic representation of the design.
    """
    if not node or not node.get('name'):
        return None

    simplified = {
        'name': node.get('name', 'Unnamed'),
        'type': node.get('type', 'UNKNOWN')
    }

    # Simplify node type for better semantic meaning
    if simplified['type'] in ['RECTANGLE', 'ELLIPSE', 'VECTOR'] and is_image_node(node):
        simplified['type'] = 'IMAGE'

    # Extract text content
    if simplified['type'] == 'TEXT':
        simplified['content'] = node.get('characters', '')

    # Recursively process children
    if 'children' in node and isinstance(node['children'], list):
        child_nodes = [simplify_node(child) for child in node['children']]
        # Filter out None values from children that were discarded
        simplified['children'] = [child for child in child_nodes if child]
        if not simplified['children']:
            del simplified['children'] # Clean up empty children arrays

    # Discard purely decorative vector nodes that add no value
    if simplified['type'] == 'VECTOR' and 'children' not in simplified:
        return None

    return simplified

# --- Figma API Interaction ---

def fetch_figma_data(api_key, file_id):
    """
    Fetches the Figma file data using the v1 API.
    """
    url = f"https://api.figma.com/v1/files/{file_id}"
    headers = {'X-Figma-Token': api_key}
    
    try:
        print(f"Fetching data for Figma file ID: {file_id}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP error codes
        print("Successfully fetched data from Figma API.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Figma API: {e}")
        if 'response' in locals() and response.status_code == 403:
            print("Authentication error (403): Please check your FIGMA_API_KEY.")
        elif 'response' in locals() and response.status_code == 404:
            print("File not found (404): Please check your FIGMA_FILE_KEY.")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from Figma API.")
        return None

# --- Main Execution Logic ---

def main():
    """
    Main function to load credentials, fetch data, process it, and save the result.
    """
    # Load environment variables from .env file
    load_dotenv()
    api_key = os.getenv('FIGMA_API_KEY')
    file_id = os.getenv('FIGMA_FILE_KEY')
    page_name = os.getenv('FIGMA_PAGE_NAME', None) # New: Optional page name

    if not api_key or not file_id:
        print("Error: FIGMA_API_KEY and FIGMA_FILE_KEY must be set in your .env file.")
        print("Please create a .env file with your credentials.")
        return

    # 1. Fetch the raw JSON from the Figma API
    raw_figma_data = fetch_figma_data(api_key, file_id)
    if not raw_figma_data:
        return # Stop execution if fetching failed

    # 2. Find the starting point for processing (main frame on the specified or first page)
    target_page = None
    if page_name:
        print(f"Attempting to find Figma page: '{page_name}'")
        for page in raw_figma_data['document']['children']:
            if page.get('type') == 'CANVAS' and page.get('name') == page_name:
                target_page = page
                break
        if not target_page:
            print(f"Error: Page '{page_name}' not found in the Figma file. "
                  f"Please check the page name and try again. "
                  f"Available pages: {[p.get('name') for p in raw_figma_data['document']['children'] if p.get('type') == 'CANVAS']}")
            return
    else:
        # Default to the first page if no page_name is provided
        target_page = raw_figma_data['document']['children'][0]
        print(f"No FIGMA_PAGE_NAME specified, defaulting to the first page: '{target_page.get('name', 'Unnamed')}'")

    # Now, extract the first 'FRAME' or 'GROUP' from the target_page as the starting point
    landing_page_frame = None
    if 'children' in target_page and isinstance(target_page['children'], list):
        for child in target_page['children']:
            # Often the main content is a FRAME or GROUP directly under the CANVAS (page)
            if child.get('type') in ['FRAME', 'GROUP']:
                landing_page_frame = child
                break
    
    if not landing_page_frame:
        print("Error: Could not find a suitable main content frame/group on the target page.")
        print("Figma structure might be different. Please check your file's layout.")
        return

    print(f"Found starting frame: '{landing_page_frame.get('name', 'Unnamed')}'")

    # 3. Process the raw data to create a simplified version
    print("Simplifying the Figma structure...")
    simplified_structure = simplify_node(landing_page_frame)
    if not simplified_structure:
        print("Processing resulted in an empty structure. Nothing to save.")
        return

    # 4. Save the simplified JSON to a file
    output_filename = 'simplified_figma.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(simplified_structure, f, indent=2)

    print("-" * 50)
    print(f"✅ Success! Simplified Figma data has been saved to '{output_filename}'.")
    print("This file is now ready to be used as a high-quality prompt for your LLM.")
    print("-" * 50)


if __name__ == '__main__':
    main()