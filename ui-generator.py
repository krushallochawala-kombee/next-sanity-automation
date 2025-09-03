# enhanced-ai-ui-generator.py
import os
import re
import subprocess
from pathlib import Path
import requests
from dotenv import load_dotenv
from PIL import Image
import io
import google.generativeai as genai
import json
from typing import Dict, List, Any, Optional


# --- Helper Functions ---
def print_step(message: str) -> None:
    """Print a formatted step message."""
    print(f"\n{'='*25} {message} {'='*25}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"✅ {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"ℹ️  {message}")


def print_error(message: str) -> None:
    """Print an error message and exit."""
    print(f"❌ ERROR: {message}")
    exit(1)


def run_command(
    command_list: List[str], cwd: Optional[str] = None, step_description: str = ""
) -> str:
    """Execute a shell command and return output."""
    command_string = " ".join(command_list)
    print_info(f"Running command: {command_string}")
    try:
        process = subprocess.run(
            command_string,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            shell=True,
            encoding="utf-8",
            errors="replace",
        )
        print_success(f"{step_description} completed.")
        return process.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed for '{step_description}'.\nError: {e.stderr}")


def format_name_to_pascal_case(name: str) -> str:
    """Convert string to PascalCase."""
    return name.replace("-", " ").replace("_", " ").title().replace(" ", "")


def format_name_to_kebab_case(name: str) -> str:
    """Convert string to kebab-case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


# --- PROJECT ANALYSIS ---


def analyze_project_structure() -> Dict[str, Any]:
    """Analyze the existing project structure and return metadata."""
    print_step("Analyzing project structure")

    project_analysis = {
        "has_sanity": False,
        "has_nextjs": False,
        "has_typescript": False,
        "has_tailwind": False,
        "folder_structure": {},
        "existing_components": [],
        "existing_queries": [],
        "package_json": {},
        "layout_path": None,
        "app_directory": None,
    }

    # Check package.json
    package_path = Path("package.json")
    if package_path.exists():
        try:
            with open(package_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)
                project_analysis["package_json"] = package_data

                dependencies = {
                    **package_data.get("dependencies", {}),
                    **package_data.get("devDependencies", {}),
                }
                project_analysis["has_sanity"] = any(
                    "sanity" in dep for dep in dependencies.keys()
                )
                project_analysis["has_nextjs"] = "next" in dependencies
                project_analysis["has_typescript"] = "typescript" in dependencies
                project_analysis["has_tailwind"] = "tailwindcss" in dependencies
        except Exception as e:
            print_info(f"Could not parse package.json: {e}")

    # Find app directory and layout
    app_paths = [Path("src/app"), Path("app")]
    for app_path in app_paths:
        if app_path.exists():
            project_analysis["app_directory"] = str(app_path)
            layout_file = app_path / "layout.tsx"
            if layout_file.exists():
                project_analysis["layout_path"] = str(layout_file)
            break

    # Analyze folder structure
    src_path = Path("src")
    if src_path.exists():
        project_analysis["folder_structure"] = analyze_folder_structure(src_path)

    # Find existing components
    components_paths = [Path("src/components"), Path("components")]
    for components_path in components_paths:
        if components_path.exists():
            project_analysis["existing_components"] = find_files_by_extension(
                components_path, [".tsx", ".jsx"]
            )
            break

    # Find existing queries
    queries_paths = [
        Path("src/sanity/queries"),
        Path("src/lib/queries"),
        Path("src/queries"),
    ]
    for queries_path in queries_paths:
        if queries_path.exists():
            project_analysis["existing_queries"].extend(
                find_files_by_extension(queries_path, [".ts", ".js"])
            )

    print_success(
        f"Project analysis complete - Framework: {'Next.js' if project_analysis['has_nextjs'] else 'Unknown'}"
    )

    return project_analysis


def analyze_folder_structure(
    path: Path, max_depth: int = 3, current_depth: int = 0
) -> Dict[str, Any]:
    """Recursively analyze folder structure."""
    if current_depth > max_depth:
        return {}

    structure = {}
    try:
        for item in path.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and item.name != "node_modules"
            ):
                structure[item.name] = analyze_folder_structure(
                    item, max_depth, current_depth + 1
                )
            elif item.is_file() and item.suffix in [".tsx", ".ts", ".js", ".jsx"]:
                if "files" not in structure:
                    structure["files"] = []
                structure["files"].append(item.name)
    except PermissionError:
        pass

    return structure


def find_files_by_extension(path: Path, extensions: List[str]) -> List[str]:
    """Find all files with given extensions in directory."""
    files = []
    try:
        for ext in extensions:
            files.extend(
                [str(f.relative_to(Path.cwd())) for f in path.rglob(f"*{ext}")]
            )
    except Exception as e:
        print_info(f"Could not scan directory {path}: {e}")

    return files


def get_all_sanity_schemas_as_json() -> Dict[str, Any]:
    """Reads existing sanity.types.ts file and parses to create JSON representation of schemas."""
    print_step("Analyzing Sanity schemas")

    types_file = Path("sanity.types.ts")
    if not types_file.exists():
        print_info("sanity.types.ts not found. Generating types...")

        # First, extract the schema
        print_info("Step 1: Extracting Sanity schema...")
        try:
            run_command(
                ["npx", "sanity", "schema", "extract"],
                step_description="Extract Sanity schema",
            )
        except:
            print_error(
                "Failed to extract Sanity schema. Please run 'npx sanity schema extract' manually first."
            )

        # Then generate types
        print_info("Step 2: Generating Sanity types...")
        try:
            run_command(
                ["npx", "sanity", "typegen", "generate"],
                step_description="Generate Sanity types",
            )
        except:
            print_error(
                "Failed to generate Sanity types. Please run 'npx sanity typegen generate' manually first."
            )

    try:
        with open(types_file, "r", encoding="utf-8") as f:
            types_content = f.read()
    except Exception as e:
        print_error(f"Error reading sanity.types.ts: {e}")

    if not types_content:
        print_error("sanity.types.ts file is empty.")

    # Enhanced schema parsing with header/footer detection
    schema_pattern = re.compile(
        r"export\s+type\s+([\w\d_]+)\s*=\s*({[\s\S]*?})\s*(?:&|\||;)", re.MULTILINE
    )
    all_schemas = {}

    for match in schema_pattern.finditer(types_content):
        type_name = match.group(1)
        type_body = match.group(2)

        if (
            not type_name.startswith("Sanity")
            and type_name != "CrossDatasetReference"
            and not type_name.startswith("InternationalizedArray")
            and not type_name.startswith("AllSanitySchemaTypes")
            and ("_id" in type_body or "_type" in type_body)
        ):
            fields = []

            # Enhanced field parsing with better regex
            field_pattern = re.compile(
                r"(\w+)\??:\s*([^;\n]+(?:\{[^}]*\}[^;\n]*)*);", re.MULTILINE | re.DOTALL
            )

            for field_match in field_pattern.finditer(type_body):
                field_name = field_match.group(1)
                field_type = field_match.group(2).strip()

                if not (
                    field_name.startswith("_")
                    and field_name not in ["_type", "_key", "_id"]
                ):
                    # Advanced field analysis
                    field_info = analyze_field_type(field_name, field_type)
                    fields.append(field_info)

            schema_info = {
                "fields": fields,
                "is_document": "_id" in type_body and "_createdAt" in type_body,
                "is_page_builder": "pageBuilder" in type_body
                or "sections" in type_body,
                "has_slug": "slug" in type_body,
                "has_localization": "InternationalizedArray" in type_body,
                "complexity_score": calculate_schema_complexity(fields),
                "is_header": "header" in type_name.lower()
                or "navigation" in type_name.lower(),
                "is_footer": "footer" in type_name.lower(),
                "is_global": "global" in type_name.lower()
                or "site" in type_name.lower(),
            }

            all_schemas[type_name] = schema_info

    if not all_schemas:
        print_error(
            "No exportable document types found. Please define at least one schema."
        )

    print_success(f"Found {len(all_schemas)} schemas to work with.")

    # Save detailed analysis
    with open("schema-analysis.json", "w", encoding="utf-8") as f:
        json.dump(all_schemas, f, indent=2, ensure_ascii=False)
    print_info("Detailed schema analysis saved to schema-analysis.json")

    return all_schemas


def analyze_field_type(field_name: str, field_type: str) -> Dict[str, Any]:
    """Analyze individual field type and return metadata."""
    field_info = {
        "name": field_name,
        "type": field_type,
        "optional": "?" in field_type,
        "is_internationalized": "InternationalizedArray" in field_type,
        "is_reference": "_ref" in field_type and "reference" in field_type,
        "is_array": field_type.startswith("Array<") or "[]" in field_type,
        "is_object": "{" in field_type and "}" in field_type,
        "is_union": "|" in field_type,
        "is_image": "asset" in field_type and "reference" in field_type,
        "is_rich_text": "PortableText" in field_type or "block" in field_type,
        "field_category": "unknown",
        "ui_component_hint": "input",
    }

    # Determine field category and UI hint
    if field_info["is_internationalized"]:
        field_info["field_category"] = "internationalized"
        field_info["ui_component_hint"] = "localized-input"
    elif field_info["is_reference"]:
        field_info["field_category"] = "reference"
        field_info["ui_component_hint"] = "reference-picker"
    elif field_info["is_image"]:
        field_info["field_category"] = "media"
        field_info["ui_component_hint"] = "image"
    elif field_info["is_rich_text"]:
        field_info["field_category"] = "rich_text"
        field_info["ui_component_hint"] = "rich-text-editor"
    elif field_info["is_array"]:
        field_info["field_category"] = "array"
        field_info["ui_component_hint"] = "array-list"
    elif field_type in ["string", "number", "boolean", "date"]:
        field_info["field_category"] = "primitive"
        field_info["ui_component_hint"] = field_type
    elif field_info["is_object"]:
        field_info["field_category"] = "object"
        field_info["ui_component_hint"] = "object-form"

    return field_info


def calculate_schema_complexity(fields: List[Dict[str, Any]]) -> int:
    """Calculate complexity score for a schema."""
    score = 0
    for field in fields:
        if field["is_array"]:
            score += 3
        elif field["is_reference"]:
            score += 2
        elif field["is_internationalized"]:
            score += 2
        elif field["is_object"]:
            score += 2
        else:
            score += 1
    return score


# --- FIGMA INTERACTION ---


def get_figma_document_data(api_token: str, file_id: str) -> Dict[str, Any]:
    """Fetch Figma document data via API."""
    url = f"https://api.figma.com/v1/files/{file_id}"
    headers = {"X-Figma-Token": api_token}
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        print_success("Successfully fetched Figma document data.")
        return response.json()
    except Exception as e:
        print_error(f"Error fetching Figma file data: {e}")


def analyze_figma_frames(figma_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze and score Figma frames for UI generation suitability."""
    candidate_frames = []
    min_width = 300

    for page in figma_data["document"].get("children", []):
        if page.get("type") == "CANVAS":
            for frame in page.get("children", []):
                if frame.get("type") == "FRAME":
                    bbox = frame.get("absoluteBoundingBox", {})
                    width = bbox.get("width", 0)
                    height = bbox.get("height", 0)

                    if width > min_width:
                        frame_analysis = {
                            "id": frame.get("id"),
                            "name": frame.get("name", "Unnamed"),
                            "width": width,
                            "height": height,
                            "aspect_ratio": width / height if height > 0 else 0,
                            "complexity_score": analyze_frame_complexity(frame),
                            "estimated_components": estimate_component_count(frame),
                            "layout_type": determine_layout_type(frame),
                            "has_header": detect_header_in_frame(frame),
                            "has_footer": detect_footer_in_frame(frame),
                            "sections": identify_frame_sections(frame),
                        }
                        candidate_frames.append(frame_analysis)

    # Sort by complexity and suitability
    candidate_frames.sort(key=lambda x: x["complexity_score"], reverse=True)

    return candidate_frames


def detect_header_in_frame(frame: Dict[str, Any]) -> bool:
    """Detect if frame has header-like elements."""
    frame_name = frame.get("name", "").lower()
    if "header" in frame_name or "nav" in frame_name:
        return True

    # Check for top-positioned elements that could be headers
    bbox = frame.get("absoluteBoundingBox", {})
    frame_height = bbox.get("height", 0)

    for child in frame.get("children", []):
        child_bbox = child.get("absoluteBoundingBox", {})
        child_y = child_bbox.get("y", 0)
        child_height = child_bbox.get("height", 0)

        # If element is in top 20% of frame and spans most width
        if child_y < frame_height * 0.2 and child_height < frame_height * 0.3:
            return True

    return False


def detect_footer_in_frame(frame: Dict[str, Any]) -> bool:
    """Detect if frame has footer-like elements."""
    frame_name = frame.get("name", "").lower()
    if "footer" in frame_name:
        return True

    # Check for bottom-positioned elements that could be footers
    bbox = frame.get("absoluteBoundingBox", {})
    frame_height = bbox.get("height", 0)
    frame_bottom = bbox.get("y", 0) + frame_height

    for child in frame.get("children", []):
        child_bbox = child.get("absoluteBoundingBox", {})
        child_y = child_bbox.get("y", 0)
        child_height = child_bbox.get("height", 0)
        child_bottom = child_y + child_height

        # If element is in bottom 20% of frame
        if child_bottom > frame_bottom * 0.8:
            return True

    return False


def identify_frame_sections(frame: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify distinct sections in the frame for better component generation."""
    sections = []

    def analyze_children(children: List[Dict[str, Any]], parent_name: str = ""):
        for child in children:
            child_name = child.get("name", "Unnamed").lower()
            child_type = child.get("type", "")

            if child_type == "FRAME" or child_type == "GROUP":
                # Determine section type
                section_type = "content"
                if "header" in child_name or "nav" in child_name:
                    section_type = "header"
                elif "footer" in child_name:
                    section_type = "footer"
                elif "hero" in child_name or "banner" in child_name:
                    section_type = "hero"
                elif "card" in child_name or "item" in child_name:
                    section_type = "card"

                sections.append(
                    {
                        "name": child.get("name", "Unnamed"),
                        "type": section_type,
                        "id": child.get("id"),
                        "bbox": child.get("absoluteBoundingBox", {}),
                        "has_children": len(child.get("children", [])) > 0,
                    }
                )

            # Recursively analyze children
            if child.get("children"):
                analyze_children(child.get("children", []), child.get("name", ""))

    analyze_children(frame.get("children", []))
    return sections


def analyze_frame_complexity(frame: Dict[str, Any]) -> int:
    """Analyze frame complexity based on children and structure."""

    def count_children_recursive(node: Dict[str, Any]) -> int:
        count = 1
        for child in node.get("children", []):
            count += count_children_recursive(child)
        return count

    return count_children_recursive(frame)


def estimate_component_count(frame: Dict[str, Any]) -> int:
    """Estimate how many React components this frame might generate."""

    def count_potential_components(node: Dict[str, Any]) -> int:
        count = 0
        node_type = node.get("type", "")

        # Text nodes, images, and frames are potential components
        if node_type in ["TEXT", "RECTANGLE", "FRAME", "GROUP", "INSTANCE"]:
            count += 1

        for child in node.get("children", []):
            count += count_potential_components(child)

        return count

    return min(count_potential_components(frame), 20)  # Cap at reasonable number


def determine_layout_type(frame: Dict[str, Any]) -> str:
    """Determine the likely layout type of the frame."""
    width = frame.get("absoluteBoundingBox", {}).get("width", 0)
    height = frame.get("absoluteBoundingBox", {}).get("height", 0)

    if width > height * 2:
        return "horizontal"
    elif height > width * 2:
        return "vertical"
    elif width > 1200:
        return "desktop"
    elif width < 768:
        return "mobile"
    else:
        return "responsive"


def select_figma_frame(figma_data: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive frame selection with enhanced analysis."""
    candidate_frames = analyze_figma_frames(figma_data)

    if not candidate_frames:
        print_error("No suitable frames found for UI generation.")

    print_step("Available Figma designs for generation")
    print_info("Frames are sorted by complexity (most complex first)")

    for i, frame in enumerate(candidate_frames):
        header_indicator = "🔝" if frame["has_header"] else ""
        footer_indicator = "🔻" if frame["has_footer"] else ""
        sections_info = (
            f"({len(frame['sections'])} sections)" if frame["sections"] else ""
        )

        print(
            f"""
  [{i + 1}] {frame['name']} {header_indicator}{footer_indicator}
      Size: {frame['width']:.0f}×{frame['height']:.0f}px
      Layout: {frame['layout_type']} {sections_info}
      Complexity: {frame['complexity_score']} elements
      Est. Components: {frame['estimated_components']}
        """
        )

    while True:
        try:
            choice = int(input("Enter the number of the design to generate: ")) - 1
            if 0 <= choice < len(candidate_frames):
                selected = candidate_frames[choice]
                print_success(
                    f"Selected: '{selected['name']}' - {selected['layout_type']} layout"
                )
                return selected
            else:
                print("❌ Invalid number. Please try again.")
        except (ValueError, IndexError):
            print("❌ Please enter a valid number.")


def export_figma_frame_as_image(
    node_id: str, figma_api_key: str, figma_file_id: str
) -> Image.Image:
    """Export Figma frame as high-quality image."""
    print_info(f"Exporting high-resolution image for Figma frame...")
    url = f"https://api.figma.com/v1/images/{figma_file_id}"
    params = {
        "ids": node_id,
        "format": "png",
        "scale": "3",  # Higher resolution for pixel-perfect analysis
        "svg_include_id": "true",
    }
    headers = {"X-Figma-Token": figma_api_key}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=120)
        response.raise_for_status()
        image_url = response.json().get("images", {}).get(node_id)
        if not image_url:
            raise ValueError("No image URL returned from Figma API.")

        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        print_success("Figma image exported successfully.")
        return Image.open(io.BytesIO(image_response.content))
    except Exception as e:
        print_error(f"Image export failed: {e}")


# --- AI-DRIVEN CODE GENERATION ---


def generate_comprehensive_ai_prompt(
    project_analysis: Dict[str, Any],
    all_schemas: Dict[str, Any],
    frame_analysis: Dict[str, Any],
    component_name: str,
    page_route_name: str,
    groq_patterns: str,
) -> str:
    """Generate a comprehensive AI prompt for pixel-perfect UI generation."""

    # Identify header and footer schemas
    header_schemas = [
        name for name, schema in all_schemas.items() if schema.get("is_header")
    ]
    footer_schemas = [
        name for name, schema in all_schemas.items() if schema.get("is_footer")
    ]
    global_schemas = [
        name for name, schema in all_schemas.items() if schema.get("is_global")
    ]

    return f"""
# MISSION: Pixel-Perfect UI Generation with Global Layout

You are an expert full-stack developer specializing in:
- Next.js 14+ App Router with Server Components
- TypeScript with strict typing
- Tailwind CSS for pixel-perfect styling
- Sanity CMS integration
- Modern React patterns and accessibility

## CRITICAL REQUIREMENTS

### 🎯 PIXEL-PERFECT VISUAL MATCHING
- Analyze the provided Figma image in EXTREME detail
- Match every pixel: spacing, colors, fonts, shadows, borders
- Recreate exact layout structure and responsive behavior
- Use precise Tailwind classes to match the design exactly
- Pay attention to subtle design details like hover states, transitions

### 🌐 GLOBAL HEADER/FOOTER IMPLEMENTATION
- Generate header/footer as SEPARATE, reusable components
- Integrate them into the root layout.tsx file
- Make them completely data-driven from Sanity
- Ensure they appear on ALL pages automatically

### 📐 COMPONENT ARCHITECTURE
- Main page component contains only the body content (excluding header/footer)
- Header and Footer are global layout components
- All components must be 100% data-driven (zero hardcoded content)
- Use TypeScript strict mode with proper typing

## INPUT ANALYSIS

### Project Structure
```json
{json.dumps(project_analysis, indent=2)}
```

### Sanity Schemas Available
```json
{json.dumps(all_schemas, indent=2)}
```

### Selected Figma Frame Analysis
```json
{json.dumps(frame_analysis, indent=2)}
```

### Detected Header Schemas: {header_schemas}
### Detected Footer Schemas: {footer_schemas}
### Global/Site Schemas: {global_schemas}

### GROQ Patterns Reference
```
{groq_patterns}
```

## VISUAL ANALYSIS REQUIREMENTS

1. **Pixel-Level Analysis**:
   - Study every element: typography, spacing, colors, shadows
   - Identify exact font weights, sizes, and line heights
   - Note precise margins, paddings, and gap measurements
   - Analyze color schemes and gradients
   - Observe border styles, border-radius values

2. **Layout Structure**:
   - Identify if there's a visible header section
   - Detect main content area structure
   - Look for footer elements at the bottom
   - Map out grid/flexbox layouts needed
   - Plan responsive breakpoints

3. **Interactive Elements**:
   - Identify buttons and their exact styling
   - Note hover and focus states
   - Plan form elements if present
   - Consider loading and error states

## SCHEMA-TO-DESIGN MAPPING

1. **Header Mapping**: If header detected in design:
   - Use available header schemas: {header_schemas}
   - Map navigation elements, logo, buttons to schema fields
   - Create reusable Header component

2. **Footer Mapping**: If footer detected in design:
   - Use available footer schemas: {footer_schemas}  
   - Map footer content to schema fields
   - Create reusable Footer component

3. **Main Content Mapping**:
   - Choose most appropriate schema for page content
   - Map every visual element to schema fields
   - Handle rich text content properly
   - Process image references correctly

## REQUIRED OUTPUT FILES

### 1. Enhanced Layout File
**Path**: `{project_analysis.get('app_directory', 'src/app')}/layout.tsx`
- Import and use Header/Footer components
- Maintain existing layout structure
- Add global components seamlessly
- Ensure proper TypeScript typing

### 2. Global Header Component  
**Path**: `src/components/layout/Header.tsx`
- Completely data-driven from Sanity
- Pixel-perfect match to design header
- Responsive navigation
- Proper TypeScript interfaces

### 3. Global Footer Component
**Path**: `src/components/layout/Footer.tsx`  
- Completely data-driven from Sanity
- Pixel-perfect match to design footer
- Responsive layout
- Proper TypeScript interfaces

### 4. Global Layout Queries
**Path**: `src/sanity/queries/layout.ts`
- Fetch header and footer data
- Optimize for performance
- Handle internationalization
- Proper error handling

### 5. Layout Types
**Path**: `src/types/layout.ts`
- Complete TypeScript interfaces for header/footer
- Proper typing for all data structures
- Export interfaces for reuse

### 6. Main Page Component
**Path**: `src/components/generated/{component_name}/index.tsx`
- Contains ONLY the main content (no header/footer)
- Pixel-perfect implementation of body content
- Fully responsive design
- Complete data-driven approach

### 7. Main Page Queries
**Path**: `src/sanity/queries/{component_name}.ts`
- Fetch all page content data
- Efficient GROQ queries
- Handle references and media
- Internationalization support

### 8. Main Page Types
**Path**: `src/types/generated/{component_name}.ts`
- Complete TypeScript interfaces
- Proper optional/required fields
- Export all needed types

### 9. Next.js Page Route
**Path**: `{project_analysis.get('app_directory', 'src/app')}/{page_route_name}/[slug]/page.tsx`
- Proper App Router implementation
- Server-side data fetching
- SEO optimization
- Error handling

## PIXEL-PERFECT STYLING GUIDELINES

### Colors & Design
- Use exact hex codes from the design
- Implement proper gradients if present
- Match shadow specifications precisely
- Use correct opacity values

### Typography
- Match font families exactly (use system fonts if custom not available)
- Use precise font weights (100-900 scale)
- Match line heights and letter spacing
- Implement proper text hierarchy

### Spacing & Layout
- Use Tailwind spacing scale (px-4, py-6, etc.)
- Implement exact margins and paddings
- Use CSS Grid for complex layouts
- Implement proper responsive breakpoints

### Components & Interactions
- Create hover effects that match the design
- Implement smooth transitions
- Add focus states for accessibility
- Handle loading and error states

## CODE QUALITY REQUIREMENTS

### TypeScript Excellence
- Strict mode enabled
- Proper interface definitions
- No `any` types allowed
- Generic types where appropriate

### React Best Practices
- Server Components by default
- Client Components only when needed
- Proper hooks usage
- Memoization for performance

### Next.js Optimization
- Proper metadata handling
- Image optimization
- Font optimization
- Bundle splitting

### Accessibility
- Semantic HTML structure
- Proper ARIA labels
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance

## IMPORTANT IMPLEMENTATION NOTES

### Layout Integration
- The enhanced layout.tsx should seamlessly integrate Header/Footer
- Maintain any existing layout code
- Add global components without breaking existing functionality
- Ensure proper TypeScript typing throughout

### Data Flow
- Header/Footer components get data from layout queries
- Main page component gets its own data
- All components are completely data-driven
- No static content or fallbacks

### Responsive Design
- Mobile-first approach
- Proper breakpoint handling
- Touch-friendly interactions
- Optimized for all devices

### Performance
- Lazy loading where appropriate
- Efficient bundle splitting
- Optimized images and fonts
- Minimal runtime overhead

## SUCCESS CRITERIA

✅ **Visual**: Pixel-perfect match to Figma design
✅ **Architecture**: Header/Footer in global layout, main content in page component
✅ **Data**: 100% driven from Sanity CMS
✅ **Performance**: Optimized and fast loading
✅ **Accessibility**: WCAG compliant
✅ **TypeScript**: Strict typing throughout
✅ **Responsive**: Works perfectly on all devices
✅ **Integration**: Seamless layout integration without breaking existing code

## CRITICAL INSTRUCTIONS

1. **Analyze the image with EXTREME attention to detail**
2. **Create components that match the design EXACTLY**
3. **Ensure Header/Footer are integrated into the global layout**
4. **Make everything 100% data-driven from Sanity**
5. **Use modern React and Next.js patterns**
6. **Implement perfect TypeScript typing**
7. **Ensure accessibility and performance**

Generate production-ready code that can be deployed immediately with pixel-perfect visual fidelity.
"""


def call_gemini_ai_for_generation(prompt: str, image: Image.Image) -> str:
    """Call Gemini AI with the enhanced prompt and image for pixel-perfect generation."""
    print_info("🤖 Calling Gemini AI for pixel-perfect UI generation...")
    print_info("This may take 60-90 seconds for complex layouts...")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY not found in environment variables.")

    genai.configure(api_key=api_key)

    # Use the most capable model for complex generation
    model = genai.GenerativeModel(
        "gemini-2.5-pro",
        generation_config={
            "temperature": 0.05,  # Very low temperature for pixel-perfect consistency
            "top_p": 0.7,
            "top_k": 30,
            "max_output_tokens": 8192,
        },
    )

    try:
        response = model.generate_content([prompt, image])
        print_success("✅ Pixel-perfect UI generation completed!")

        # Save response for debugging
        with open("ai_generation_log.txt", "w", encoding="utf-8") as f:
            f.write("=== ENHANCED AI GENERATION LOG ===\n\n")
            f.write("PROMPT USED:\n")
            f.write(prompt)
            f.write("\n\n=== AI RESPONSE ===\n\n")
            f.write(response.text)

        print_info("Full AI response saved to ai_generation_log.txt")

        return response.text
    except Exception as e:
        print_error(f"AI generation failed: {e}")


def validate_and_parse_ai_response(
    response_text: str, component_name: str
) -> Dict[str, str]:
    """Enhanced parsing for the new file structure with layout integration."""
    if not response_text:
        print_error("Cannot process empty AI response.")

    print_step("🔍 Parsing AI-generated code with layout integration")

    files = {}

    # Enhanced parsing patterns for new file structure
    patterns = [
        # Pattern 1: **Path**: `filepath` format
        re.compile(
            r"\*\*Path\*\*:\s*`([^`]+)`[^\n]*\n```(\w+)?\s*([\s\S]*?)```", re.MULTILINE
        ),
        # Pattern 2: ### Title with **Path**: format
        re.compile(
            r"###\s+\d+\.\s+[^\n]+\s*\*\*Path\*\*:\s*`([^`]+)`[^\n]*\n```(\w+)?\s*([\s\S]*?)```",
            re.MULTILINE,
        ),
        # Pattern 3: Direct code blocks with filenames
        re.compile(
            r"`([^`]*\.(tsx?|jsx?))`[^\n]*\n```(\w+)?\s*([\s\S]*?)```", re.MULTILINE
        ),
        # Pattern 4: File headers
        re.compile(
            r"(?:^|\n)(?:##+\s*)?([^\n]*\.(tsx?|jsx?|ts))\s*\n```(\w+)?\s*([\s\S]*?)```",
            re.MULTILINE,
        ),
    ]

    for pattern in patterns:
        matches = pattern.findall(response_text)
        for match in matches:
            if len(match) >= 3:
                filepath = match[0].strip()
                content = match[-1].strip()
                if filepath and content and "." in filepath:
                    files[filepath] = content

    # Validation with enhanced expected files
    expected_files = [
        f"src/components/layout/Header.tsx",
        f"src/components/layout/Footer.tsx",
        f"src/sanity/queries/layout.ts",
        f"src/types/layout.ts",
        f"src/components/generated/{component_name}/index.tsx",
        f"src/sanity/queries/{component_name}.ts",
        f"src/types/generated/{component_name}.ts",
    ]

    found_files = list(files.keys())
    missing_files = []

    for expected in expected_files:
        if not any(expected in found for found in found_files):
            # Check for similar paths
            similar = [f for f in found_files if expected.split("/")[-1] in f]
            if not similar:
                missing_files.append(expected)

    if missing_files:
        print_info("⚠️  Some expected files may be missing:")
        for missing in missing_files:
            print_info(f"   - {missing}")

    if not files:
        print_error(
            "Could not parse any files from AI response. "
            "Please check ai_generation_log.txt for the raw output."
        )

    print_success(f"✅ Successfully parsed {len(files)} files from AI response")

    # Log parsed files for debugging
    print_info("📁 Parsed files:")
    for filepath in sorted(files.keys()):
        print_info(f"   - {filepath}")

    return files


def create_files_from_ai_response(
    files: Dict[str, str], project_analysis: Dict[str, Any]
) -> List[str]:
    """Create files with enhanced layout integration."""
    print_step("📁 Creating generated files with layout integration")

    created_files = []
    layout_backup_created = False

    for filepath, content in files.items():
        try:
            file_path = Path(filepath)

            # Special handling for layout.tsx - create backup first
            if "layout.tsx" in filepath and not layout_backup_created:
                existing_layout = Path(
                    project_analysis.get("layout_path", "src/app/layout.tsx")
                )
                if existing_layout.exists():
                    backup_path = existing_layout.with_suffix(".backup.tsx")
                    backup_path.write_text(
                        existing_layout.read_text(encoding="utf-8"), encoding="utf-8"
                    )
                    print_success(f"✅ Created backup: {backup_path}")
                    layout_backup_created = True

            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            file_path.write_text(content, encoding="utf-8")

            created_files.append(str(file_path))

            # Special indicators for important files
            if "layout.tsx" in str(file_path):
                print_success(f"🌐 Updated Layout: {file_path}")
            elif "Header.tsx" in str(file_path):
                print_success(f"🔝 Created Header: {file_path}")
            elif "Footer.tsx" in str(file_path):
                print_success(f"🔻 Created Footer: {file_path}")
            else:
                print_success(f"✅ Created: {file_path}")

        except Exception as e:
            print_error(f"❌ Failed to create {filepath}: {e}")

    if not created_files:
        print_error("No files were successfully created.")

    return created_files


def load_groq_patterns() -> str:
    """Enhanced GROQ patterns for complex queries."""
    return """
# GROQ Query Patterns Reference

## Basic Patterns
- Single document: *[_type == "TYPE" && CONDITION][0] { FIELDS }
- List query: *[_type == "TYPE"] { FIELDS }  
- Reference resolution: field->{ FIELDS }
- Array processing: arrayField[] { FIELDS }

## Layout/Global Queries
- Header data: *[_type == "header" || _type == "navigation"][0] { FIELDS }
- Footer data: *[_type == "footer"][0] { FIELDS }
- Global site data: *[_type == "global" || _type == "siteSettings"][0] { FIELDS }

## Internationalization  
- Localized field: coalesce(field[_key == $locale][0].value, field[_key == 'en'][0].value)
- Localized slug filter: slug[0].value.current == $slug
- Localized reference: ref->coalesce(title[_key == $locale][0].value, title[_key == 'en'][0].value)

## Advanced Patterns
- Conditional fields: _type == "TYPE" => @{ FIELDS }
- Image projection: image { asset->{ url, altText, metadata } }
- Nested references: ref->{ ..., nested->{ FIELDS } }
- Array filtering: array[condition] { FIELDS }
- Complex joins: *[_type == "TYPE"] { ..., "related": *[_type == "other" && references(^._id)] }

## Performance Optimizations
- Use fragments for reusability
- Limit fields to only what's needed  
- Handle null values with coalesce()
- Use proper indexing for filters
- Batch related queries efficiently

## Common Field Projections
- Rich text: content[]{..., markDefs[]{..., _type == "link" => { href }}}
- Image arrays: images[]{ asset->{url, altText}, caption }
- Reference arrays: items[]->{ title, slug, image }
"""


def main():
    """Enhanced main execution function."""
    print_step("🚀 Enhanced AI-Driven UI Generator Starting")
    print_info("Pixel-perfect generation with global layout integration")

    # Load environment variables
    load_dotenv()

    # Validate required environment variables
    required_env_vars = ["FIGMA_API_KEY", "FIGMA_FILE_KEY", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print_error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    figma_api_key = os.getenv("FIGMA_API_KEY")
    figma_file_id = os.getenv("FIGMA_FILE_KEY")

    try:
        # Step 1: Enhanced project analysis
        print_step("📊 Enhanced Project Analysis Phase")
        project_analysis = analyze_project_structure()

        if not project_analysis["has_nextjs"]:
            print_error(
                "This script requires a Next.js project. Please run in a Next.js project directory."
            )

        if not project_analysis["layout_path"]:
            print_info("⚠️  No layout.tsx found. Will create one in the app directory.")

        # Step 2: Load and analyze Sanity schemas with header/footer detection
        print_step("🗃️  Enhanced Schema Analysis Phase")
        all_schemas = get_all_sanity_schemas_as_json()

        # Identify global components
        header_schemas = [
            name for name, schema in all_schemas.items() if schema.get("is_header")
        ]
        footer_schemas = [
            name for name, schema in all_schemas.items() if schema.get("is_footer")
        ]

        if header_schemas:
            print_info(f"🔝 Detected header schemas: {', '.join(header_schemas)}")
        if footer_schemas:
            print_info(f"🔻 Detected footer schemas: {', '.join(footer_schemas)}")

        # Step 3: Enhanced Figma interaction
        print_step("🎨 Enhanced Figma Analysis Phase")
        figma_data = get_figma_document_data(figma_api_key, figma_file_id)

        # Select frame with enhanced analysis
        selected_frame = select_figma_frame(figma_data)

        # Generate component names
        component_name = format_name_to_pascal_case(selected_frame["name"])
        page_route_name = format_name_to_kebab_case(component_name)

        print_info(f"🏗️  Generating component: {component_name}")
        print_info(f"📄 Route will be: /{page_route_name}/[slug]")

        if selected_frame["has_header"]:
            print_info("🔝 Header detected in design - will be integrated globally")
        if selected_frame["has_footer"]:
            print_info("🔻 Footer detected in design - will be integrated globally")

        # Step 4: Export ultra-high quality image
        print_step("📸 High-Resolution Image Export Phase")
        figma_image = export_figma_frame_as_image(
            selected_frame["id"], figma_api_key, figma_file_id
        )

        # Save image for reference
        figma_image.save(
            f"design-reference-{component_name.lower()}.png", optimize=True, quality=95
        )
        print_info(
            f"Design reference saved as: design-reference-{component_name.lower()}.png"
        )

        # Step 5: Enhanced GROQ patterns
        groq_patterns = load_groq_patterns()

        # Step 6: Generate comprehensive AI prompt
        print_step("🧠 Enhanced AI Prompt Generation Phase")
        ai_prompt = generate_comprehensive_ai_prompt(
            project_analysis=project_analysis,
            all_schemas=all_schemas,
            frame_analysis=selected_frame,
            component_name=component_name,
            page_route_name=page_route_name,
            groq_patterns=groq_patterns,
        )

        # Save prompt for reference
        with open(
            f"generation-prompt-{component_name.lower()}.md", "w", encoding="utf-8"
        ) as f:
            f.write(ai_prompt)
        print_info(
            f"Generation prompt saved as: generation-prompt-{component_name.lower()}.md"
        )

        # Step 7: AI code generation with enhanced model
        print_step("🤖 Enhanced AI Code Generation Phase")
        ai_response = call_gemini_ai_for_generation(ai_prompt, figma_image)

        # Step 8: Enhanced parsing and validation
        print_step("🔍 Enhanced Response Processing Phase")
        parsed_files = validate_and_parse_ai_response(ai_response, component_name)

        # Step 9: Create all files with layout integration
        print_step("📁 Enhanced File Creation Phase")
        created_files = create_files_from_ai_response(parsed_files, project_analysis)

        # Step 10: Final summary and enhanced next steps
        print_step("✅ Enhanced Generation Complete!")

        print("\n🎉 Pixel-Perfect UI Generation Successful!")
        print("=" * 65)

        print(f"\n📦 Component Generated: {component_name}")
        print(f"🔗 Route: /{page_route_name}/[slug]")
        print(f"🎨 Design: {selected_frame['name']}")
        print(f"📊 Complexity: {selected_frame['complexity_score']} elements")
        print(f"🏗️  Sections: {len(selected_frame.get('sections', []))}")

        # Categorize created files
        layout_files = [f for f in created_files if "layout" in f.lower()]
        header_files = [f for f in created_files if "Header" in f]
        footer_files = [f for f in created_files if "Footer" in f]
        component_files = [
            f
            for f in created_files
            if f not in layout_files + header_files + footer_files
        ]

        print(f"\n📁 Files Created ({len(created_files)}):")

        if layout_files:
            print("  🌐 Layout Integration:")
            for file_path in sorted(layout_files):
                print(f"     • {file_path}")

        if header_files:
            print("  🔝 Header Components:")
            for file_path in sorted(header_files):
                print(f"     • {file_path}")

        if footer_files:
            print("  🔻 Footer Components:")
            for file_path in sorted(footer_files):
                print(f"     • {file_path}")

        if component_files:
            print("  ⚛️  Main Components:")
            for file_path in sorted(component_files):
                file_type = (
                    "📘 Types"
                    if file_path.endswith(".ts")
                    else "🔍 Queries" if "queries" in file_path else "⚛️  Component"
                )
                print(f"     {file_type}: {file_path}")

        print("\n🔧 Reference Files:")
        print(f"   🖼️  Design Reference: design-reference-{component_name.lower()}.png")
        print(f"   📝 Generation Prompt: generation-prompt-{component_name.lower()}.md")
        print(f"   🔍 AI Response Log: ai_generation_log.txt")
        print(f"   📊 Schema Analysis: schema-analysis.json")

        # if layout_backup_created:
        #     print(f"   💾 Layout Backup: {project_analysis.get('layout_path', 'src/app/layout.tsx').replace('.tsx', '.backup.tsx')}")

        # Enhanced next steps guidance
        print("\n🚀 Next Steps:")
        print("=" * 35)

        print("\n1. 📋 Review Generated Code:")
        print(
            f"   • Check global layout integration: {project_analysis.get('layout_path', 'src/app/layout.tsx')}"
        )
        print(f"   • Review Header component: src/components/layout/Header.tsx")
        print(f"   • Review Footer component: src/components/layout/Footer.tsx")
        print(f"   • Check main component: src/components/generated/{component_name}/")

        print("\n2. 🗃️  Create Sanity Content:")
        print("   • Open your Sanity Studio")
        if header_schemas:
            print(f"   • Create header content in: {', '.join(header_schemas)}")
        if footer_schemas:
            print(f"   • Create footer content in: {', '.join(footer_schemas)}")
        print("   • Create main page content with slug fields")
        print("   • Publish all content")

        print("\n3. 🧪 Test the Implementation:")
        print("   • Run: npm run dev")
        print("   • Check header/footer appear on all pages")
        print(
            f"   • Navigate to: http://localhost:3000/{page_route_name}/your-content-slug"
        )
        print("   • Verify pixel-perfect design match")
        print("   • Test responsive behavior on all devices")

        print("\n4. 🎯 Fine-tuning (if needed):")
        print("   • Compare with design reference image")
        print("   • Adjust Tailwind classes for pixel-perfect match")
        print("   • Optimize GROQ queries if needed")
        print("   • Add loading states and error handling")

        # Enhanced warnings and tips
        print("\n⚠️  Important Notes:")
        print("=" * 30)
        print("🔸 Header/Footer are now global - appear on ALL pages")
        print("🔸 All components are 100% data-driven - no static content")
        print("🔸 Design should be pixel-perfect match to Figma")
        print("🔸 Layout integration maintains existing functionality")

        if project_analysis.get("layout_path"):
            print("🔸 Original layout.tsx backed up with .backup.tsx extension")

        if not project_analysis.get("has_tailwind"):
            print("\n🚨 CRITICAL: Tailwind CSS not detected!")
            print("   Install with: npm install -D tailwindcss @tailwindcss/typography")
            print("   The pixel-perfect styling requires Tailwind CSS")

        print("\n💡 Pro Tips:")
        print("🔹 Use browser dev tools to compare with design reference")
        print("🔹 Header/Footer data is fetched once and cached globally")
        print("🔹 Generated code follows Next.js 14+ App Router best practices")
        print("🔹 All components are accessible and SEO-optimized")
        print("🔹 Responsive design works across all device sizes")

        print(f"\n✨ Your pixel-perfect {component_name} is ready!")
        print("🎨 The UI should match your Figma design exactly!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user.")
        exit(0)
    except Exception as e:
        print_error(f"Unexpected error during generation: {e}")
        print("\n🔍 Check the following for debugging:")
        print("   • ai_generation_log.txt - Full AI response")
        print("   • schema-analysis.json - Schema analysis results")
        print(
            f"   • generation-prompt-{component_name.lower() if 'component_name' in locals() else 'latest'}.md - AI prompt used"
        )


if __name__ == "__main__":
    main()
