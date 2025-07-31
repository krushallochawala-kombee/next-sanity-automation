# ui-generator.py
import os
import re
import subprocess
from pathlib import Path
import requests
from dotenv import load_dotenv
from PIL import Image
import io
import google.generativeai as genai
import time


# --- Helper Functions ---
def print_step(message):
    """Prints a formatted step header."""
    print(f"\n{'='*25} {message} {'='*25}")


def print_success(message):
    """Prints a success message."""
    print(f"✅ {message}")


def print_info(message):
    """Prints an informational message."""
    print(f"ℹ️  {message}")


def print_error(message):
    """Prints an error message and exits the script."""
    print(f"❌ ERROR: {message}")
    exit(1)


def run_command(command_list, cwd=None, step_description=""):
    """Runs a command, captures its output, and handles errors."""
    command_string = " ".join(command_list)
    print_info(f"Running command: {command_string}")
    try:
        # Use shell=True for compatibility with npx on different systems
        process = subprocess.run(
            command_string,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            shell=True,
            encoding="utf-8",  # Force UTF-8 encoding to fix Unicode errors
            errors="ignore",  # Ignore encoding errors
        )
        print_success(f"{step_description} completed successfully.")
        return process.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed for step '{step_description}'.\nError: {e.stderr}")
    return None


# --- Type & Query Generation (from Official Sanity Types) ---


def generate_and_read_sanity_types():
    """Runs `npx sanity typegen generate` and returns the content of the generated types file."""
    print_step("Generating TypeScript types from your Sanity schemas")
    # First extract the schema, then generate types
    run_command(
        ["npx", "sanity", "schema", "extract"],
        step_description="Sanity Schema Extraction",
    )
    run_command(
        ["npx", "sanity", "typegen", "generate"],
        step_description="Sanity Type Generation",
    )

    types_file = Path("sanity.types.ts")
    if not types_file.exists():
        print_error(
            "`sanity.types.ts` was not created. Ensure your Sanity project is configured correctly and you have at least one schema."
        )

    print_success("Successfully read generated Sanity types.")
    return types_file.read_text()


def parse_types_and_select_schema(types_content: str):
    """Parses the generated type definitions and presents an interactive menu to select a schema."""
    # This regex finds exported types that are objects, typical for document schemas
    schema_pattern = re.compile(
        r"export\s+type\s+([\w\d_]+)\s*=\s*({[\s\S]*?});", re.MULTILINE
    )

    schemas = []
    for match in schema_pattern.finditer(types_content):
        type_name = match.group(1)
        # Filter out Sanity's internal utility types to present a clean list
        if not type_name.startswith("Sanity") and type_name != "CrossDatasetReference":
            schemas.append({"name": type_name, "definition": match.group(2)})

    if not schemas:
        print_error(
            "No exportable document types found in `sanity.types.ts`. Please define at least one schema in your `schemaTypes` directory."
        )

    print_step("Please select a schema to generate the UI for")
    for i, schema in enumerate(schemas):
        print(f"  [{i + 1}] {schema['name']}")
    print("-" * 60)

    while True:
        try:
            choice = input("Enter the number of the schema: ")
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(schemas):
                selected = schemas[choice_index]
                print_success(f"You selected schema: '{selected['name']}'")
                return selected
            else:
                print("Invalid number. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number from the list.")


def generate_groq_from_type(schema_name: str, type_definition: str) -> str:
    """Generates a GROQ query based on the fields present in a TypeScript interface."""
    print_step(f"Generating GROQ Query for '{schema_name}'")

    # Regex to find property names in the TypeScript type definition
    field_pattern = re.compile(r"(\w+)\??:\s*.*;", re.MULTILINE)
    fields = []

    # Iterate over the lines of the type definition to extract field names
    for line in type_definition.split("\n"):
        match = field_pattern.match(line.strip())
        if match:
            field_name = match.group(1)
            # Exclude Sanity's internal metadata fields
            if field_name not in ["_id", "_type", "_rev", "_createdAt", "_updatedAt"]:
                field_type_str = line.split(":")[1].strip()
                # If a field is an image, expand its asset reference in the query
                if "SanityImage" in field_type_str:
                    fields.append(
                        f"'{field_name}': {field_name}{{ asset->{{ url, metadata }} }}"
                    )
                # If a field appears to be a reference, expand it
                elif "->" in field_name or "reference" in field_name.lower():
                    fields.append(f"'{field_name}': {field_name}->")
                else:
                    fields.append(f"'{field_name}': {field_name}")

    query_fields_str = ",\n    ".join(fields)

    # Use the PascalCase schema name for the query function name
    query_function_name = f"get{schema_name}BySlug"
    # The document type in Sanity is usually the lowercase version
    document_type = schema_name.lower()

    query = f"""
import type {{ {schema_name} }} from './types'

// This query is designed to fetch all the data needed for the {schema_name} component.
// It is based on the automatically generated TypeScript type.
export const {query_function_name}Query = `*[_type == "{document_type}" && slug.current == $slug][0]{{
    _id,
    {query_fields_str}
}}`
"""
    print_success("GROQ query generated successfully.")
    return query


# --- FIGMA INTERACTION ---


def get_figma_document_data(api_token: str, file_id: str):
    """Fetches Figma document data using the API."""
    url = f"https://api.figma.com/v1/files/{file_id}"
    headers = {"X-Figma-Token": api_token}
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        print_success("Successfully fetched Figma document data.")
        return response.json()
    except Exception as e:
        print_error(f"Error fetching Figma file data: {e}")


def select_figma_frame(figma_data: dict):
    """Presents an interactive menu to select a Figma frame."""
    candidate_frames = []
    # A good candidate for a page is a wide frame directly on a canvas
    min_width_for_candidate = 400
    for page in figma_data["document"].get("children", []):
        if page.get("type") == "CANVAS":
            for frame in page.get("children", []):
                if (
                    frame.get("type") == "FRAME"
                    and frame.get("absoluteBoundingBox", {}).get("width", 0)
                    > min_width_for_candidate
                ):
                    candidate_frames.append(
                        {
                            "id": frame.get("id"),
                            "name": frame.get("name", "Unnamed Frame"),
                            "page_name": page.get("name", "Unnamed Page"),
                        }
                    )
    if not candidate_frames:
        print_error(
            "No suitable top-level frames found in Figma file. Ensure there are frames with a width > 400px directly on a page."
        )

    print_step("Please select the corresponding Figma design for your schema")
    for i, frame in enumerate(candidate_frames):
        print(f"  [{i + 1}] {frame['name']} (on page: '{frame['page_name']}')")

    while True:
        try:
            choice = int(input("Enter the number of the design: ")) - 1
            if 0 <= choice < len(candidate_frames):
                selected = candidate_frames[choice]
                print_success(f"You selected Figma design: '{selected['name']}'")
                return selected
            else:
                print("Invalid number.")
        except (ValueError, IndexError):
            print("Invalid input.")


def export_figma_frame_as_image(node_id: str, figma_api_key: str, figma_file_id: str):
    """Exports a Figma frame as a PNG image."""
    print_info(f"Exporting image for Figma node {node_id}...")
    url = f"https://api.figma.com/v1/images/{figma_file_id}"
    params = {"ids": node_id, "format": "png", "scale": "1.5"}
    headers = {"X-Figma-Token": figma_api_key}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=120)
        response.raise_for_status()
        image_url = response.json().get("images", {}).get(node_id)
        if not image_url:
            raise ValueError("No image URL returned from API.")

        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        print_success("Figma image exported successfully.")
        return Image.open(io.BytesIO(image_response.content))
    except Exception as e:
        print_error(f"Image export for node {node_id} failed: {e}")


# --- AI-DRIVEN UI GENERATION ---


def generate_ui_prompt(type_definition_with_name: str) -> str:
    """Generates a focused prompt for the AI to create the UI component."""
    return f"""
You are an expert front-end developer specializing in creating pixel-perfect, fully dynamic UIs with Next.js and Tailwind CSS.
Your task is to create a React component that is visually identical to the provided Figma image. This component must not contain any static text or hardcoded content; all content must be rendered from a `data` prop.

**INPUT 1: The Data Contract.**
The component you create will receive a `data` prop. This prop's structure is defined by the following TypeScript type. You must create UI elements for every field in this type.

```typescript
{type_definition_with_name}
```

**INPUT 2: The Visual Design.**
An image of the Figma design is being provided. This is the visual target. You must replicate it perfectly.

**YOUR TASK: Generate a single React component file.**
- Component Name: Name the component based on the TypeScript type name.
- Props: The component must accept a single prop: data, which is typed with the interface provided above.
- No Static Content: Do not hardcode any text (e.g., "Welcome to our site"). Instead, use the corresponding field from the data prop (e.g., {{data.title}}). Every visible piece of content must come from the data prop.
- Styling: Use Tailwind CSS exclusively for all styling. The result must be responsive and visually identical to the image.
- Data Rendering:
  - Use <Image> from next/image to render fields of type SanityImage. Assume a urlFor helper exists.
  - Use <PortableText> from @portabletext/react to render fields of type PortableTextBlock[].
  - Render all other fields from the data prop in the appropriate places in the design.

**OUTPUT FORMAT:**
Provide the response as a single, complete markdown code block.
```tsx
// FILEPATH: component.tsx
// ... code for React component ...
```
"""


def call_gemini_api_for_ui(prompt: str, image: Image.Image):
    """Calls the Gemini API to generate UI code based on prompt and image."""
    print_info("Calling Gemini API for UI generation. This may take a moment...")
    api_key = os.getenv("GEMINI_API_KEY")  # Match your .env file
    if not api_key:
        print_error("GEMINI_API_KEY not found.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(
            [prompt, image], generation_config={"temperature": 0.2}
        )
        print_success("Gemini API call successful.")
        return response.text
    except Exception as e:
        if "429" in str(e) and "quota" in str(e):
            print_info("⚠️ Gemini API quota exceeded. Using demo component for testing.")
            return "DEMO_COMPONENT_FOR_TESTING"
        else:
            print_error(f"Error calling Gemini API: {e}")


def parse_ai_response_for_component(response_text: str) -> str:
    """Extracts the component code from the AI response markdown block."""
    print_info("Analyzing AI response...")

    # Debug: Save the response to see what we got
    with open("ai_response_debug.txt", "w", encoding="utf-8") as f:
        f.write(response_text)
    print_info("AI response saved to 'ai_response_debug.txt' for debugging")

    # Try multiple patterns to find the component code
    patterns = [
        r"```tsx\s*\n\s*//\s*FILEPATH:\s*component\.tsx\n([\s\S]*?)\n```",  # Original pattern
        r"```tsx\s*\n([\s\S]*?)\n```",  # Any tsx code block
        r"```typescript\s*\n([\s\S]*?)\n```",  # TypeScript code block
        r"```jsx\s*\n([\s\S]*?)\n```",  # JSX code block
        r"```react\s*\n([\s\S]*?)\n```",  # React code block
        r"```\s*\n([\s\S]*?)\n```",  # Any code block
    ]

    for i, pattern in enumerate(patterns):
        match = re.search(pattern, response_text, re.MULTILINE | re.IGNORECASE)
        if match:
            print_success(f"Found component code using pattern {i + 1}")
            component_code = match.group(1).strip()

            # Basic validation - ensure it looks like a React component
            if (
                "export default" in component_code
                or "function " in component_code
                or "const " in component_code
            ):
                return component_code

    # If no patterns work, create a basic template
    print_info(
        "Could not parse AI response. Creating a basic template component. "
        "Check 'ai_response_debug.txt' to see the actual AI response."
    )

    # Return a basic template that the user can modify
    return """'use client'

import React from 'react'
import Image from 'next/image'
import { PortableText } from '@portabletext/react'

interface Props {
  data: any // Replace with your actual type
}

export default function GeneratedComponent({ data }: Props) {
  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Generated Component</h2>
      <p className="text-gray-600">
        This is a basic template. Check ai_response_debug.txt to see the AI response
        and manually edit this component to match your Figma design.
      </p>
      <pre className="mt-4 p-4 bg-gray-100 rounded text-sm overflow-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}"""


# --- Main Orchestration ---
def main():
    """Main function that orchestrates the entire UI generation process."""
    load_dotenv()

    # Step 1: Generate types and let the user select a schema
    types_content = generate_and_read_sanity_types()
    selected_schema = parse_types_and_select_schema(types_content)
    schema_name_pascal = selected_schema["name"]

    # Step 2: Generate the GROQ query from the selected schema's type
    groq_query_code = generate_groq_from_type(
        schema_name_pascal, selected_schema["definition"]
    )

    # Step 3: Let the user select the corresponding Figma design
    figma_api_key = os.getenv("FIGMA_API_KEY")
    figma_file_id = os.getenv("FIGMA_FILE_KEY")  # Match your .env file
    if not figma_api_key or not figma_file_id:
        print_error("FIGMA_API_KEY and FIGMA_FILE_KEY must be set in your .env file.")

    figma_data = get_figma_document_data(figma_api_key, figma_file_id)
    selected_frame = select_figma_frame(figma_data)
    figma_image = export_figma_frame_as_image(
        selected_frame["id"], figma_api_key, figma_file_id
    )

    # Step 4: Generate the UI component using AI
    # We pass the full type definition to the AI so it knows what data to expect
    type_definition_for_prompt = (
        f"export type {schema_name_pascal} = {selected_schema['definition']};"
    )
    ui_prompt = generate_ui_prompt(type_definition_for_prompt)
    ai_ui_response = call_gemini_api_for_ui(ui_prompt, figma_image)
    react_component_code = parse_ai_response_for_component(ai_ui_response)

    # Step 5: Create all the generated files in an organized folder
    print_step("Creating Final Component Module")
    output_dir = Path(f"src/components/generated/{schema_name_pascal}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create the types file, including necessary imports
    (output_dir / "types.ts").write_text(
        f"import type {{ Image as SanityImage, PortableTextBlock }} from 'sanity';\n\n{type_definition_for_prompt}"
    )
    print_success(f"Created file: {output_dir / 'types.ts'}")

    # Create the query file
    (output_dir / "query.ts").write_text(groq_query_code)
    print_success(f"Created file: {output_dir / 'query.ts'}")

    # Create the component file
    (output_dir / "component.tsx").write_text(react_component_code)
    print_success(f"Created file: {output_dir / 'component.tsx'}")

    print("\n🚀 Hybrid code generation complete!")
    print(f"   A fully dynamic component module has been created in: {output_dir}")
    print("\nNext Steps:")
    print(
        f"1. **Create a page route** in `src/app/` to use your new `{schema_name_pascal}` component."
    )
    print(
        f"2. In that page, import and use the `get{schema_name_pascal}BySlugQuery` to fetch data."
    )
    print(f"3. Pass the fetched data to your new component.")
    print(
        f"4. Go to your Sanity Studio, create content for the '{schema_name_pascal}' type, and publish it."
    )


if __name__ == "__main__":
    main()
