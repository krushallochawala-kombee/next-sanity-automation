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
import json


# --- Helper Functions ---
def print_step(message):
    print(f"\n{'='*25} {message} {'='*25}")


def print_success(message):
    print(f"✅ {message}")


def print_info(message):
    print(f"ℹ️  {message}")


def print_error(message):
    print(f"❌ ERROR: {message}")
    exit(1)


def run_command(command_list, cwd=None, step_description=""):
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
            errors="replace",  # Replace problematic characters instead of failing
        )
        print_success(f"{step_description} completed.")
        return process.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed for '{step_description}'.\nError: {e.stderr}")


def format_name_to_pascal_case(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title().replace(" ", "")


# --- DATA STRUCTURE ANALYSIS ---


def get_all_sanity_schemas_as_json():
    """Reads existing sanity.types.ts file or generates it, then parses to create JSON representation of schemas."""
    print_step("Analyzing all available Sanity schemas")

    # Check if sanity.types.ts already exists
    types_file = Path("sanity.types.ts")
    if not types_file.exists():
        print_info("sanity.types.ts not found. Generating types...")
        print_info("Please run this command manually first:")
        print_info("npx sanity typegen generate")
        print_error(
            "sanity.types.ts file not found. Please generate it first with 'npx sanity typegen generate'"
        )

    # Read the types file
    try:
        with open(types_file, "r", encoding="utf-8") as f:
            types_content = f.read()
    except Exception as e:
        print_error(f"Error reading sanity.types.ts: {e}")

    if not types_content:
        print_error("sanity.types.ts file is empty.")

    # Enhanced schema parsing with better TypeScript type handling
    schema_pattern = re.compile(
        r"export\s+type\s+([\w\d_]+)\s*=\s*({[\s\S]*?})\s*(?:&|\||\s)*;", re.MULTILINE
    )
    all_schemas = {}

    for match in schema_pattern.finditer(types_content):
        type_name = match.group(1)
        type_body = match.group(2)

        # Skip utility types and focus on actual schema types
        if (
            not type_name.startswith("Sanity")
            and type_name != "CrossDatasetReference"
            and not type_name.startswith("InternationalizedArray")
            and not type_name.startswith("AllSanitySchemaTypes")
            and ("_id" in type_body or "_type" in type_body)
        ):
            fields = []

            # More sophisticated field parsing to handle complex TypeScript types
            # Handle both single-line and multi-line field definitions
            field_pattern = re.compile(
                r"(\w+)\??:\s*([^;\n]+(?:\{[^}]*\}[^;\n]*)*);", re.MULTILINE | re.DOTALL
            )

            for field_match in field_pattern.finditer(type_body):
                field_name = field_match.group(1)
                field_type = field_match.group(2).strip()

                # Skip internal Sanity fields except _type and _key
                if not (
                    field_name.startswith("_") and field_name not in ["_type", "_key"]
                ):
                    # Analyze field type to determine if it's internationalized
                    is_internationalized = "InternationalizedArray" in field_type
                    is_reference = "_ref" in field_type and "reference" in field_type
                    is_array = field_type.startswith("Array<")
                    is_simple_type = field_type in ["string", "number", "boolean"]

                    # Determine field category for GROQ generation
                    field_category = "unknown"
                    if is_internationalized:
                        if "StringValue" in field_type:
                            field_category = "internationalized_string"
                        elif "TextValue" in field_type:
                            field_category = "internationalized_text"
                        elif "ImageValue" in field_type:
                            field_category = "internationalized_image"
                        elif "UrlValue" in field_type:
                            field_category = "internationalized_url"
                        elif "SlugValue" in field_type:
                            field_category = "internationalized_slug"
                    elif is_reference:
                        field_category = "reference"
                    elif is_array and not is_internationalized:
                        field_category = "array"
                    elif is_simple_type:
                        field_category = "simple"

                    fields.append(
                        {
                            "name": field_name,
                            "type": field_type,
                            "optional": "?" in field_match.group(0),
                            "is_internationalized": is_internationalized,
                            "is_reference": is_reference,
                            "is_array": is_array,
                            "field_category": field_category,
                        }
                    )

            all_schemas[type_name] = {
                "fields": fields,
                "is_document": "_id" in type_body and "_createdAt" in type_body,
                "is_page_builder": "pageBuilder" in type_body,
            }

    if not all_schemas:
        print_error(
            "No exportable document types found. Please define at least one schema."
        )

    print_success(f"Found {len(all_schemas)} schemas to work with.")

    # Print schema summary for debugging
    for schema_name, schema_info in all_schemas.items():
        if schema_info["is_document"]:
            print_info(
                f"📄 Document: {schema_name} ({len(schema_info['fields'])} fields)"
            )
        else:
            print_info(
                f"🧩 Object: {schema_name} ({len(schema_info['fields'])} fields)"
            )

    # Save schemas to a JSON file for debugging
    with open("schema.json", "w", encoding="utf-8") as f:
        json.dump(all_schemas, f, indent=2, ensure_ascii=False)
    print_info("Schema analysis saved to schema.json")

    return all_schemas


# --- FIGMA INTERACTION ---


def get_figma_document_data(api_token: str, file_id: str):
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
    candidate_frames = []
    min_width = 400
    for page in figma_data["document"].get("children", []):
        if page.get("type") == "CANVAS":
            for frame in page.get("children", []):
                if (
                    frame.get("type") == "FRAME"
                    and frame.get("absoluteBoundingBox", {}).get("width", 0) > min_width
                ):
                    candidate_frames.append(
                        {"id": frame.get("id"), "name": frame.get("name", "Unnamed")}
                    )

    if not candidate_frames:
        print_error(f"No suitable frames found (width > {min_width}px).")

    print_step("Please select the Figma design to generate")
    for i, frame in enumerate(candidate_frames):
        print(f"  [{i + 1}] {frame['name']}")

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
    print_info(f"Exporting image for Figma node {node_id}...")
    url = f"https://api.figma.com/v1/images/{figma_file_id}"
    params = {"ids": node_id, "format": "png", "scale": "1.5"}
    headers = {"X-Figma-Token": figma_api_key}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=120)
        response.raise_for_status()
        image_url = response.json().get("images", {}).get(node_id)
        if not image_url:
            raise ValueError("No image URL returned.")
        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        print_success("Figma image exported successfully.")
        return Image.open(io.BytesIO(image_response.content))
    except Exception as e:
        print_error(f"Image export for node {node_id} failed: {e}")


# --- AI-DRIVEN CODE GENERATION ---


def generate_ai_prompt(all_schemas_json: str, component_name: str) -> str:
    return f"""
You are an expert full-stack developer who reverse-engineers web designs into fully-functional, data-driven applications. Your task is to analyze a Figma design, intelligently map its content to a list of available Sanity schemas, and generate all the necessary code, including a perfectly tailored GROQ query.

**INPUT 1: The Visual Design (as an image)**
This is the visual "blueprint." Your generated component must be a pixel-perfect, responsive replica.

**INPUT 2: All Available Sanity Schemas**
This JSON object describes every piece of data you are allowed to use. You must map the content you see in the design to the fields in these schemas.
```json
{all_schemas_json}
```

YOUR TASK: Generate a complete, self-contained module for a component named '{component_name}'.

**CRITICAL SCHEMA ANALYSIS:**
The schemas use INTERNATIONALIZED ARRAYS extensively. Each field with internationalized content is structured as:
- `Array<{{ _key: string }} & InternationalizedArrayStringValue>` for strings
- `Array<{{ _key: string }} & InternationalizedArrayTextValue>` for text
- `Array<{{ _key: string }} & InternationalizedArrayImageValue>` for images
- `Array<{{ _key: string }} & InternationalizedArraySlugValue>` for slugs

**CRITICAL REQUIREMENT - NO STATIC CONTENT:**
- 🚨 **ZERO static/hardcoded content allowed** - EVERYTHING must come from the Sanity query
- 🚨 **NO placeholder text** like "Lorem ipsum", "Sample text", or "Your content here"
- 🚨 **NO hardcoded values** - all text, images, links, and data must be dynamic
- 🚨 **NO fallback static content** - use empty strings or null checks instead

**GLOBAL HEADER & FOOTER REQUIREMENT:**
- 🌐 **Header and Footer are GLOBAL components** - same across all pages
- 🌐 **Generate ONE header and ONE footer** from Figma design analysis
- 🌐 **Header/Footer data comes from Sanity** - use Header and Footer schemas
- 🌐 **Include header/footer in ALL page queries** - fetch global data
- 🌐 **Create separate Header.tsx and Footer.tsx components** for reusability
- 🚨 **ZERO static content in Header/Footer** - if no data from Sanity, render NOTHING
- 🚨 **NO fallback text** - no "Home", "About", "Contact" hardcoded links
- 🚨 **NO placeholder logos** - if no logo from Sanity, show nothing
- 🚨 **NO default navigation** - only show navigation items from Sanity data

**IMPORTANT DATA STRUCTURE REQUIREMENTS:**
- ALL text fields are internationalized arrays, NOT PortableText
- Images are structured as: `{{ value?: {{ asset?: {{ url: string; altText?: string }} }} }}`
- Use helper functions to extract values from internationalized arrays
- Links are objects with externalUrl and internalLink (reference with slug)
- The Page schema has a pageBuilder array with different section types
- If data is missing, show empty state or nothing - NO static fallbacks

Step 1: Data-to-Design Mapping (Your internal thought process):
Analyze the visual design. Identify all dynamic elements (headings, text blocks, images, lists, buttons).
Look at the available schemas and their fields. Find the best match.
Decide which schema is the primary document type for this component (e.g., 'Page'). This will be the entry point for your query.
🌐 **ALWAYS include Header and Footer data** in your queries - they are global components.
🌐 **Identify header/footer elements** in the Figma design and map them to Header/Footer schemas.

Step 2: Generate the Code (Your output):

TypeScript Types (types.ts):
- Create interfaces that match the internationalized array structure
- Image fields should have: `{{ value?: {{ asset?: {{ url: string; altText?: string }} }} }}`
- Text fields should be: `Array<{{ _key: string; value?: string }}>`
- Include proper Link interface with externalUrl and internalLink

Smart GROQ Query (query.ts):
- CRITICAL: For internationalized arrays, project the WHOLE field, not individual values
- ❌ NEVER use: `title[0].value` or `field[0].value.asset->` - These are INVALID GROQ syntax
- ✅ CORRECT: For internationalized text fields, use: `title` (project whole field)
- ✅ CORRECT: For internationalized image fields, use: `image {{ value {{ asset->{{url, altText}} }} }}`
- ✅ CORRECT: For filtering, use: `slug[0].value.current == $slug` (slug IS internationalized)
- Handle internationalized content in components with helper functions
- NO JavaScript template literals (${{variables}}) - pure GROQ only
- For pageBuilder sections, use conditional projections based on _type
- 🌐 **ALWAYS include Header and Footer** in your query - they are global components
- 🌐 **Fetch Header data**: `"header": *[_type == "header"][0] {{ ... }}`
- 🌐 **Fetch Footer data**: `"footer": *[_type == "footer"][0] {{ ... }}`

React Component (component.tsx):
- DETECT schema structure: ALL fields are internationalized arrays
- Create getInternationalizedString() helper with proper type checking
- Create getInternationalizedImage() helper for image fields
- Handle both data structures gracefully with appropriate helpers
- CRITICAL: Filter out null values from arrays: `data?.array?.filter(item => item !== null)`
- CRITICAL: Use proper type guards and unknown type instead of any
- Include 'use client' directive at the top
- 🚨 **NO static fallback content** - if data is missing, render nothing or empty state
- 🚨 **NO hardcoded text** - all content must come from the query data
- Use index-based keys for arrays without _key properties
- Only render elements if data exists - use conditional rendering extensively
- 🌐 **Include Header and Footer components** - import and render them
- 🌐 **Pass header/footer data as props** to the global components
- 🚨 **CRITICAL: Header/Footer must be 100% data-driven** - NO static content whatsoever
- 🚨 **If header/footer data is missing, render NOTHING** - no fallback content

Next.js Page Route (page.tsx):
- CRITICAL: Use Next.js 15+ async params: `params: Promise<{{ slug: string }}>`
- CRITICAL: Await params: `const {{ slug }} = await params;`
- Import from absolute paths: '@/sanity/lib/client'
- Handle notFound() case properly
- Use proper error handling for data fetching

OUTPUT FORMAT:
⚠️ CRITICAL: You MUST provide exactly SIX code blocks in this EXACT format. Each code block must start with a FILEPATH comment line followed immediately by a code block.

**REQUIRED FORMAT - FOLLOW EXACTLY:**

// FILEPATH: types.ts
```typescript
// Define types that match the internationalized array structure
export interface InternationalizedString {{
  _key: string;
  value?: string;
}}

export interface InternationalizedImage {{
  _key: string;
  value?: {{
    asset?: {{
      url: string;
      altText?: string;
    }};
  }};
}}

// Your complete types here...
```

// FILEPATH: query.ts  
```typescript
import {{ groq }} from 'next-sanity';

export const get{component_name}DataQuery = groq`
  {{
    "page": *[_type == "page" && slug[0].value.current == $slug][0] {{
      _id,
      _type,
      title,                          // ✅ Correct: project whole internationalized field
      slug,                           // ✅ Correct: project whole internationalized field
      pageBuilder[] {{
        _key,
        _type,
        // CORRECT examples for internationalized arrays:
        _type == "herosection" => {{
          headline,                    // ✅ Correct: project whole internationalized field
          tagline,                     // ✅ Correct: project whole internationalized field  
          image {{ value {{ asset->{{url, altText}} }} }},  // ✅ Correct: internationalized image syntax
          ctaButtons[] {{
            _key,
            label,
            link {{
              internalLink->{{ slug }},
              externalUrl
            }}
          }}
        }},
        _type == "socialproofsection" => {{
          title,                       // ✅ Correct: project whole field
          description,                 // ✅ Correct: project whole field
          logos[]->{{                   // ✅ Correct: reference expansion
            name,                      // ✅ Correct: project whole field in referenced doc
            logo {{ value {{ asset->{{url, altText}} }} }}  // ✅ Correct: image in referenced doc
          }}
        }},
        _type == "featuressection" => {{
          title,
          description,
          features[]->{{
            title,
            description,
            icon {{ value {{ asset->{{url, altText}} }} }}
          }}
        }}
      }}
    }},
    "header": *[_type == "header"][0] {{  // 🌐 Global header data
      _id,
      _type,
      logo {{
        _ref,
        _type,
        name,
        logo {{ value {{ asset->{{url, altText}} }} }}
      }},
      mainNavigation[] {{
        _key,
        _type,
        label,
        link {{
          internalLink->{{ slug }},
          externalUrl
        }}
      }},
      ctaButton {{
        _key,
        _type,
        label,
        link {{
          internalLink->{{ slug }},
          externalUrl
        }}
      }}
    }},
    "footer": *[_type == "footer"][0] {{  // 🌐 Global footer data
      _id,
      _type,
      linkColumns[] {{
        _key,
        _type,
        title,
        links[] {{
          _key,
          _type,
          label,
          link {{
            internalLink->{{ slug }},
            externalUrl
          }}
        }}
      }},
      logo {{
        _ref,
        _type,
        name,
        logo {{ value {{ asset->{{url, altText}} }} }}
      }},
      copyrightText
    }},
    "siteSettings": *[_type == "siteSettings"][0] {{
      siteName,
      siteDescription
    }}
  }}
`;
```

// FILEPATH: component.tsx
```tsx
'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import type {{ /* your types */ }} from './types';

// Helper function to extract string from internationalized array
const getInternationalizedString = (data: unknown): string => {{
  if (!data) return "";
  
  // Handle internationalized array
  if (Array.isArray(data) && data.length > 0) {{
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {{
      const typedItem = firstItem as {{ value?: string }};
      return typedItem.value || "";
    }}
  }}
  
  // Handle simple string
  if (typeof data === 'string') {{
    return data;
  }}
  
  return "";
}};

// Helper function to extract image from internationalized array
const getInternationalizedImage = (data: unknown): {{ url: string; altText?: string }} | null => {{
  if (!data) return null;
  
  if (Array.isArray(data) && data.length > 0) {{
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {{
      const typedItem = firstItem as {{ value?: {{ asset?: {{ url: string; altText?: string }} }} }};
      return typedItem.value?.asset || null;
    }}
  }}
  
  return null;
}};

// CRITICAL: Always filter null values from arrays
// Example: data?.linkColumns?.filter(column => column !== null)?.map(...)

// 🚨 CRITICAL: NO STATIC CONTENT - Everything must come from data
// Only render elements if data exists - use conditional rendering
// Example: {{data?.title && <h1>{{getInternationalizedString(data.title)}}</h1>}}

// 🌐 Import global Header and Footer components
import Header from './Header';
import Footer from './Footer';

// Your main component code here...
// Include Header and Footer: <Header data={{data.header}} /> and <Footer data={{data.footer}} />
```
```

// FILEPATH: Header.tsx
```tsx
'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import type {{ HeaderData }} from './types';

// Helper functions (same as above)
const getInternationalizedString = (data: unknown): string => {{
  // ... same implementation
}};

const getInternationalizedImage = (data: unknown): {{ url: string; altText?: string }} | null => {{
  // ... same implementation
}};

interface HeaderProps {{
  data: HeaderData;
}}

export default function Header({{ data }}: HeaderProps) {{
  // 🚨 CRITICAL: If no data from Sanity, render NOTHING
  if (!data) return null;
  
  return (
    <header>
      {{/* Logo - ONLY if data exists from Sanity */}}
      {{data.logo && getInternationalizedString(data.logo.name) && (
        <div>
          {{getInternationalizedImage(data.logo.logo) && (
            <Image
              src={{getInternationalizedImage(data.logo.logo)!.url}}
              alt={{getInternationalizedString(data.logo.altText) || ''}}
              width={{100}}
              height={{50}}
            />
          )}}
          {{/* Show logo name if no image */}}
          {{!getInternationalizedImage(data.logo.logo) && (
            <span>{{getInternationalizedString(data.logo.name)}}</span>
          )}}
        </div>
      )}}
      
      {{/* Navigation - ONLY if data exists from Sanity */}}
      {{data.mainNavigation && data.mainNavigation.length > 0 && (
        <nav>
          {{data.mainNavigation
            .filter(item => getInternationalizedString(item.label)) // 🚨 Only show items with actual data
            .map((item, index) => (
            <Link 
              key={{index}} 
              href={{getInternationalizedString(item.link?.externalUrl) || '#'}}
            >
              {{getInternationalizedString(item.label)}}
            </Link>
          ))}}
        </nav>
      )}}
      
      {{/* CTA Button - ONLY if data exists from Sanity */}}
      {{data.ctaButton && getInternationalizedString(data.ctaButton.label) && (
        <button>
          {{getInternationalizedString(data.ctaButton.label)}}
        </button>
      )}}
    </header>
  );
}}
```

// FILEPATH: Footer.tsx
```tsx
'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import type {{ FooterData }} from './types';

// Helper functions (same as above)
const getInternationalizedString = (data: unknown): string => {{
  // ... same implementation
}};

const getInternationalizedImage = (data: unknown): {{ url: string; altText?: string }} | null => {{
  // ... same implementation
}};

interface FooterProps {{
  data: FooterData;
}}

export default function Footer({{ data }}: FooterProps) {{
  // 🚨 CRITICAL: If no data from Sanity, render NOTHING
  if (!data) return null;
  
  return (
    <footer>
      {{/* Footer Logo - ONLY if data exists from Sanity */}}
      {{data.logo && getInternationalizedString(data.logo.name) && (
        <div>
          {{getInternationalizedImage(data.logo.logo) && (
            <Image
              src={{getInternationalizedImage(data.logo.logo)!.url}}
              alt={{getInternationalizedString(data.logo.altText) || ''}}
              width={{100}}
              height={{50}}
            />
          )}}
          {{/* Show logo name if no image */}}
          {{!getInternationalizedImage(data.logo.logo) && (
            <span>{{getInternationalizedString(data.logo.name)}}</span>
          )}}
        </div>
      )}}
      
      {{/* Link Columns - ONLY if data exists from Sanity */}}
      {{data.linkColumns && data.linkColumns.length > 0 && (
        <div>
          {{data.linkColumns
            .filter(column => getInternationalizedString(column.title)) // 🚨 Only show columns with actual data
            .map((column, index) => (
            <div key={{index}}>
              {{getInternationalizedString(column.title) && (
                <h3>{{getInternationalizedString(column.title)}}</h3>
              )}}
              {{column.links && column.links.length > 0 && (
                <ul>
                  {{column.links
                    .filter(link => getInternationalizedString(link.label)) // 🚨 Only show links with actual data
                    .map((link, linkIndex) => (
                    <li key={{linkIndex}}>
                      <Link href={{getInternationalizedString(link.link?.externalUrl) || '#'}}>
                        {{getInternationalizedString(link.label)}}
                      </Link>
                    </li>
                  ))}}
                </ul>
              )}}
            </div>
          ))}}
        </div>
      )}}
      
      {{/* Copyright - ONLY if data exists from Sanity */}}
      {{data.copyrightText && getInternationalizedString(data.copyrightText) && (
        <p>{{getInternationalizedString(data.copyrightText)}}</p>
      )}}
    </footer>
  );
}}
```

// FILEPATH: page.tsx
```tsx
import {{ client }} from '@/sanity/lib/client';
import {{ get{component_name}DataQuery }} from '@/components/generated/{component_name}/query';
import {component_name} from '@/components/generated/{component_name}/component';
import {{ notFound }} from 'next/navigation';
import type {{ {component_name}Data }} from '@/components/generated/{component_name}/types';

interface PageProps {{
  params: Promise<{{ slug: string }}>;
}}

export default async function {component_name}Page({{ params }}: PageProps) {{
  const {{ slug }} = await params; // CRITICAL: await params in Next.js 15+
  
  const data: {component_name}Data | null = await client.fetch(get{component_name}DataQuery, {{ slug }});
  
  if (!data || !data.page) {{
    notFound();
  }}
  
  return <{component_name} data={{data}} />;
}}
```

CRITICAL REQUIREMENTS:
1. GROQ queries must use pure GROQ syntax - NO JavaScript template literals (${{variables}})
2. Next.js 15+ requires: `params: Promise<{{ slug: string }}>` and `await params`
3. Configure next.config.ts with Sanity CDN domain
4. Install required dependencies: @portabletext/react @portabletext/types
5. Use proper internationalized array handling throughout
6. 🚨 **NO static content** - everything must come from Sanity data
7. 🚨 **NO placeholder text** - use conditional rendering instead
8. 🚨 **NO hardcoded navigation** - no "Home", "About", "Contact" links
9. 🚨 **NO fallback logos** - if no logo from Sanity, show nothing
10. 🚨 **NO default copyright text** - only show if data exists in Sanity
11. 🚨 **Header/Footer must be 100% data-driven** - if no data, render nothing
12. Use proper TypeScript types
13. Test all generated queries for syntax errors

⚠️ FORMATTING REQUIREMENTS - ESSENTIAL:
1. Start each code block with: // FILEPATH: [filename]
2. Follow immediately with: ```typescript or ```tsx
3. End each code block with: ```
4. NO extra text between FILEPATH and code block
5. Provide exactly 6 code blocks (types.ts, query.ts, component.tsx, Header.tsx, Footer.tsx, page.tsx)

🚨 CRITICAL GROQ SYNTAX RULES:
- ❌ NEVER use: `field[0].value` or `field[0].value.asset->` (INVALID GROQ!)
- ✅ ALWAYS use: `field` for internationalized text and `field {{ value {{ asset->{{url, altText}} }} }}` for images
- ✅ ALWAYS use: `slug[0].value.current == $slug` for filtering (slug IS internationalized)
- The validation will REJECT queries with [0].value patterns!

**Example of correct format:**
// FILEPATH: types.ts
```typescript
[your code here]
```

// FILEPATH: query.ts
```typescript
[your code here - with CORRECT GROQ syntax!]
```

// FILEPATH: component.tsx
```tsx
[your main component code here]
```

// FILEPATH: Header.tsx
```tsx
[your header component code here]
```

// FILEPATH: Footer.tsx
```tsx
[your footer component code here]
```

// FILEPATH: page.tsx
```tsx
[your page component code here]
```
"""


def call_gemini_api(prompt: str, image: Image.Image):
    print_info("Calling Gemini API. This may take a moment...")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY not found in environment variables.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    try:
        response = model.generate_content(
            [prompt, image], generation_config={"temperature": 0.1}
        )
        print_success("Gemini API call successful.")

        # Save the response for debugging
        with open("ai_response_debug.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        print_info("AI response saved to ai_response_debug.txt for debugging")

        return response.text
    except Exception as e:
        print_error(f"Error calling Gemini API: {e}")


def validate_groq_syntax(content: str) -> tuple[bool, str]:
    """Validate GROQ query for common syntax errors."""
    errors = []

    # Check for JavaScript template literals in GROQ
    if "${" in content and "groq`" in content:
        errors.append(
            "❌ Found JavaScript template literals (${}) in GROQ query - use pure GROQ syntax only"
        )

    # CRITICAL: Check for invalid internationalized array access patterns
    import re

    # Pattern 1: field[0].value - Invalid GROQ syntax for internationalized arrays
    invalid_array_pattern = re.compile(r"\w+\[0\]\.value", re.MULTILINE)
    if invalid_array_pattern.search(content):
        errors.append(
            "❌ Found 'field[0].value' - Invalid GROQ syntax! For internationalized arrays, just use 'field' and handle in component"
        )

    # Pattern 2: field[0].value.asset-> - Invalid asset access in internationalized arrays
    invalid_asset_pattern = re.compile(r"\w+\[0\]\.value\.asset->", re.MULTILINE)
    if invalid_asset_pattern.search(content):
        errors.append(
            "❌ Found 'field[0].value.asset->' - Invalid GROQ syntax! Use 'field { value { asset->{url, altText} } }' instead"
        )

    # Pattern 3: Check for any [n].value patterns (common mistake)
    bracket_value_pattern = re.compile(r"\[\d+\]\.value", re.MULTILINE)
    if bracket_value_pattern.search(content):
        errors.append(
            "❌ Found '[n].value' pattern - Invalid GROQ syntax! For internationalized fields, project the whole field and handle in component"
        )

    # Check for malformed image projections
    if "asset->url" in content and "asset->{" not in content:
        errors.append("❌ Found 'asset->url' - should be 'asset->{url}'")

    # Check for missing closing braces
    open_braces = content.count("{")
    close_braces = content.count("}")
    if open_braces != close_braces:
        errors.append(
            f"❌ Mismatched braces: {open_braces} opening, {close_braces} closing"
        )

    # Check for slug syntax - CORRECTED for internationalized arrays
    if "slug.current ==" in content and "slug[0].value.current" not in content:
        errors.append(
            "❌ Found 'slug.current' but schema uses internationalized arrays - use 'slug[0].value.current'"
        )

    # Check for over-projection in internationalized arrays
    if "slug[].value.current" in content:
        errors.append(
            "❌ Found 'slug[].value.current' - should be 'slug[0].value.current' for filtering"
        )

    # Check for correct internationalized image syntax
    if "image {" in content and "value {" not in content:
        errors.append(
            "❌ Found 'image {' but missing 'value {' - use 'image { value { asset->{url, altText} } }'"
        )

    # Check for correct internationalized field projections
    internationalized_fields = [
        "title",
        "description",
        "headline",
        "tagline",
        "name",
        "label",
    ]
    for field in internationalized_fields:
        if f"{field}[0].value" in content:
            errors.append(
                f"❌ Found '{field}[0].value' - should be just '{field}' for internationalized arrays"
            )

    return len(errors) == 0, "\n".join(errors)


def validate_nextjs_params(content: str) -> tuple[bool, str]:
    """Validate Next.js page for proper params handling."""
    errors = []

    # Check for Next.js 15+ params
    if "params:" in content and "Promise<" not in content:
        errors.append(
            "❌ Found params without Promise<> - use 'params: Promise<{slug: string}>'"
        )

    if "const { slug } = params;" in content:
        errors.append(
            "❌ Found synchronous params access - use 'const {slug} = await params;'"
        )

    return len(errors) == 0, "\n".join(errors)


def validate_header_footer_content(content: str) -> tuple[bool, str]:
    """Validate Header and Footer components for static content."""
    errors = []

    # Check for hardcoded navigation items
    hardcoded_nav = ["Home", "About", "Contact", "Services", "Products", "Blog"]
    for nav_item in hardcoded_nav:
        if f'"{nav_item}"' in content or f"'{nav_item}'" in content:
            errors.append(
                f"❌ Found hardcoded navigation item '{nav_item}' - use only Sanity data"
            )

    # Check for hardcoded copyright text
    if "© 2024" in content or "All rights reserved" in content:
        errors.append("❌ Found hardcoded copyright text - use only Sanity data")

    # Check for hardcoded logo text
    if '"Logo"' in content or "'Logo'" in content:
        errors.append("❌ Found hardcoded logo text - use only Sanity data")

    # Check for fallback content
    if "|| 'Home'" in content or "|| 'About'" in content:
        errors.append(
            "❌ Found fallback static content - use conditional rendering instead"
        )

    return len(errors) == 0, "\n".join(errors)


def manual_parse_fallback(response_text: str):
    """Fallback manual parsing when regex patterns fail."""
    print_info("Attempting manual parsing as fallback...")

    files_found = []
    lines = response_text.split("\n")

    current_filepath = None
    current_content = []
    in_code_block = False

    for line in lines:
        # Look for FILEPATH lines
        if "FILEPATH:" in line and not in_code_block:
            # Save previous file if exists
            if current_filepath and current_content:
                content = "\n".join(current_content).strip()
                if content:
                    files_found.append((current_filepath, content))

            # Extract filepath
            current_filepath = line.split("FILEPATH:", 1)[1].strip()
            current_content = []
            continue

        # Handle code blocks
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                continue
            else:
                in_code_block = False
                continue

        # Collect content inside code blocks
        if in_code_block and current_filepath:
            current_content.append(line)

    # Don't forget the last file
    if current_filepath and current_content:
        content = "\n".join(current_content).strip()
        if content:
            files_found.append((current_filepath, content))

    print_info(f"Manual parsing found {len(files_found)} files")
    return files_found


def parse_and_create_files(
    response_text: str, component_name: str, component_dir: Path, page_dir: Path
):
    if not response_text:
        print_error("Cannot create files from empty AI response.")

    print_step(f"Creating files for '{component_name}'")
    component_dir.mkdir(parents=True, exist_ok=True)
    page_dir.mkdir(parents=True, exist_ok=True)

    # Try multiple patterns to handle different AI response formats
    file_patterns = [
        # Standard format: // FILEPATH: path
        re.compile(
            r"//\s*FILEPATH:\s*([^\n]+)\n```(?:\w+)?\n([\s\S]*?)\n```", re.MULTILINE
        ),
        # Alternative format: FILEPATH: path (without //)
        re.compile(r"FILEPATH:\s*([^\n]+)\n```(?:\w+)?\n([\s\S]*?)\n```", re.MULTILINE),
        # With language specifier: ```typescript or ```tsx
        re.compile(
            r"//\s*FILEPATH:\s*([^\n]+)\n```(?:typescript|tsx|ts|javascript|jsx|js)\n([\s\S]*?)\n```",
            re.MULTILINE,
        ),
        # More flexible whitespace handling
        re.compile(
            r"//\s*FILEPATH\s*:\s*([^\n]+)\s*\n\s*```\w*\s*\n([\s\S]*?)\n\s*```",
            re.MULTILINE,
        ),
    ]

    files_created = {}
    validation_errors = []

    # Try multiple patterns to find files
    matches = []
    pattern_used = None

    for i, pattern in enumerate(file_patterns):
        matches = list(pattern.finditer(response_text))
        if matches:
            pattern_used = i + 1
            print_info(f"Found files using pattern #{pattern_used}")
            break

    if not matches:
        print_info("⚠️  Regex patterns failed to find files. Trying fallback parsing...")

        # Debug information
        print_info("🔍 Debug Information:")
        print_info(f"Response length: {len(response_text)} characters")

        # Check for common patterns that might indicate issues
        code_blocks = response_text.count("```")
        filepath_mentions = response_text.count("FILEPATH")
        comment_mentions = response_text.count("//")

        print_info(f"Code blocks found (```): {code_blocks}")
        print_info(f"FILEPATH mentions: {filepath_mentions}")
        print_info(f"Comment markers (//): {comment_mentions}")

        # Try manual parsing as fallback
        manual_files = manual_parse_fallback(response_text)

        if manual_files:
            print_success(
                f"✅ Fallback parsing successful! Found {len(manual_files)} files"
            )
            # Convert manual parsing results to match format
            matches = []
            for filepath, content in manual_files:
                # Create a mock match object
                class MockMatch:
                    def __init__(self, fp, cont):
                        self.filepath = fp
                        self.content = cont

                    def group(self, n):
                        return self.filepath if n == 1 else self.content

                matches.append(MockMatch(filepath, content))
        else:
            # Show debug info if even manual parsing fails
            lines = response_text.split("\n")[:20]
            print_info("First 20 lines of AI response:")
            for i, line in enumerate(lines, 1):
                print_info(f"  {i:2d}: {line[:100]}{'...' if len(line) > 100 else ''}")

            print_error(
                "❌ Both regex and manual parsing failed. Check ai_response_debug.txt for the complete AI response format."
            )

    print_info(f"Found {len(matches)} files to create")

    for match in matches:
        filepath = match.group(1).strip()
        content = match.group(2).strip()

        # Extract just the filename from the full path
        filename = filepath.split("/")[-1] if "/" in filepath else filepath

        # Validate specific file types
        if filename == "query.ts":
            is_valid, error_msg = validate_groq_syntax(content)
            if not is_valid:
                validation_errors.append(f"GROQ Validation in {filename}:\n{error_msg}")

        if filename == "page.tsx":
            is_valid, error_msg = validate_nextjs_params(content)
            if not is_valid:
                validation_errors.append(
                    f"Next.js Validation in {filename}:\n{error_msg}"
                )

        if filename in ["Header.tsx", "Footer.tsx"]:
            is_valid, error_msg = validate_header_footer_content(content)
            if not is_valid:
                validation_errors.append(
                    f"Header/Footer Validation in {filename}:\n{error_msg}"
                )

        if filename == "page.tsx":
            file_path = page_dir / filename
        else:
            file_path = component_dir / filename

        file_path.write_text(content, encoding="utf-8")
        files_created[filename] = file_path
        print_success(f"Created file: {file_path}")

    # Report validation errors but don't stop - let user fix them
    if validation_errors:
        print_info("⚠️  Validation warnings found:")
        for error in validation_errors:
            print_info(error)
        print_info("Files created but may need manual fixes.")

    if len(files_created) < 6:
        print_info(
            f"⚠️  Expected 6 code blocks (types.ts, query.ts, component.tsx, Header.tsx, Footer.tsx, page.tsx), but only found {len(files_created)}."
        )
        print_info(
            "This might be normal if the AI provided a different number of files."
        )
        print_info("Check ai_response_debug.txt to see the actual AI response format.")
        if len(files_created) == 0:
            print_error(
                "No files were created. There might be a formatting issue with the AI response."
            )


def create_sample_ai_response(component_name: str):
    """Create a sample AI response file showing the expected format."""
    sample_response = f"""
This is a sample of the expected AI response format for the UI generator.

// FILEPATH: types.ts
```typescript
import {{ PortableTextBlock }} from '@portabletext/types';

export type PortableTextContent = PortableTextBlock[];

export type PageData = {{
  _id: string;
  title?: string;
  slug?: {{ current?: string }};
  content?: PortableTextContent;
}};

export type HeaderData = {{
  _id: string;
  logo?: {{
    _ref: string;
    name?: InternationalizedString[];
    logo?: InternationalizedImage[];
  }};
  mainNavigation?: Array<{{
    _key: string;
    label?: InternationalizedString[];
    link?: {{
      internalLink?: {{ slug?: InternationalizedString[] }};
      externalUrl?: InternationalizedString[];
    }};
  }}>;
  ctaButton?: {{
    label?: InternationalizedString[];
    link?: {{
      internalLink?: {{ slug?: InternationalizedString[] }};
      externalUrl?: InternationalizedString[];
    }};
  }};
}};

export type FooterData = {{
  _id: string;
  linkColumns?: Array<{{
    _key: string;
    title?: InternationalizedString[];
    links?: Array<{{
      _key: string;
      label?: InternationalizedString[];
      link?: {{
        internalLink?: {{ slug?: InternationalizedString[] }};
        externalUrl?: InternationalizedString[];
      }};
    }}>;
  }}>;
  logo?: {{
    _ref: string;
    name?: InternationalizedString[];
    logo?: InternationalizedImage[];
  }};
  copyrightText?: InternationalizedString[];
}};

export type {component_name}Data = {{
  page: PageData;
  header: HeaderData;
  footer: FooterData;
  siteSettings: {{
    siteName?: string;
    siteDescription?: string;
  }};
}};
```

// FILEPATH: query.ts
```typescript
import {{ groq }} from 'next-sanity';

export const get{component_name}DataQuery = groq`
  {{
    "page": *[_type == "page" && slug[0].value.current == $slug][0] {{
      _id,
      title,
      slug,
      content
    }},
    "header": *[_type == "header"][0] {{
      _id,
      logo {{
        _ref,
        name,
        logo {{ value {{ asset->{{url, altText}} }} }}
      }},
      mainNavigation[] {{
        _key,
        label,
        link {{
          internalLink->{{ slug }},
          externalUrl
        }}
      }},
      ctaButton {{
        label,
        link {{
          internalLink->{{ slug }},
          externalUrl
        }}
      }}
    }},
    "footer": *[_type == "footer"][0] {{
      _id,
      linkColumns[] {{
        _key,
        title,
        links[] {{
          _key,
          label,
          link {{
            internalLink->{{ slug }},
            externalUrl
          }}
        }}
      }},
      logo {{
        _ref,
        name,
        logo {{ value {{ asset->{{url, altText}} }} }}
      }},
      copyrightText
    }},
    "siteSettings": *[_type == "siteSettings"][0] {{
      siteName,
      siteDescription
    }}
  }}
`;
```

// FILEPATH: component.tsx
```tsx
'use client';

import React from 'react';
import {{ PortableText }} from '@portabletext/react';
import type {{ {component_name}Data }} from './types';

interface Props {{
  data: {component_name}Data;
}}

export default function {component_name}({{ data }}: Props) {{
  return (
    <>
      {{/* Global Header */}}
      {{data.header && <Header data={{data.header}} />}}
      
      <main>
        {{data.page?.title && (
          <h1>{{getInternationalizedString(data.page.title)}}</h1>
        )}}
        {{data.page?.content && (
          <PortableText value={{data.page.content}} />
        )}}
      </main>
      
      {{/* Global Footer */}}
      {{data.footer && <Footer data={{data.footer}} />}}
    </>
  );
}}
```

// FILEPATH: Header.tsx
```tsx
'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import type {{ HeaderData }} from './types';

// Helper functions (same as above)
const getInternationalizedString = (data: unknown): string => {{
  if (!data) return "";
  if (Array.isArray(data) && data.length > 0) {{
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {{
      const typedItem = firstItem as {{ value?: string }};
      return typedItem.value || "";
    }}
  }}
  if (typeof data === 'string') {{
    return data;
  }}
  return "";
}};

interface HeaderProps {{
  data: HeaderData;
}}

export default function Header({{ data }}: HeaderProps) {{
  // 🚨 CRITICAL: If no data from Sanity, render NOTHING
  if (!data) return null;
  
  return (
    <header>
      {{/* Logo - ONLY if data exists from Sanity */}}
      {{data.logo && getInternationalizedString(data.logo.name) && (
        <div>
          <h1>{{getInternationalizedString(data.logo.name)}}</h1>
        </div>
      )}}
      
      {{/* Navigation - ONLY if data exists from Sanity */}}
      {{data.mainNavigation && data.mainNavigation.length > 0 && (
        <nav>
          {{data.mainNavigation
            .filter(item => getInternationalizedString(item.label)) // 🚨 Only show items with actual data
            .map((item, index) => (
            <Link key={{index}} href={{getInternationalizedString(item.link?.externalUrl) || '#'}}>
              {{getInternationalizedString(item.label)}}
            </Link>
          ))}}
        </nav>
      )}}
      
      {{/* CTA Button - ONLY if data exists from Sanity */}}
      {{data.ctaButton && getInternationalizedString(data.ctaButton.label) && (
        <button>
          {{getInternationalizedString(data.ctaButton.label)}}
        </button>
      )}}
    </header>
  );
}}
```

// FILEPATH: Footer.tsx
```tsx
'use client';

import React from 'react';
import Link from 'next/link';
import type {{ FooterData }} from './types';

// Helper functions (same as above)
const getInternationalizedString = (data: unknown): string => {{
  if (!data) return "";
  if (Array.isArray(data) && data.length > 0) {{
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {{
      const typedItem = firstItem as {{ value?: string }};
      return typedItem.value || "";
    }}
  }}
  if (typeof data === 'string') {{
    return data;
  }}
  return "";
}};

interface FooterProps {{
  data: FooterData;
}}

export default function Footer({{ data }}: FooterProps) {{
  // 🚨 CRITICAL: If no data from Sanity, render NOTHING
  if (!data) return null;
  
  return (
    <footer>
      {{/* Link Columns - ONLY if data exists from Sanity */}}
      {{data.linkColumns && data.linkColumns.length > 0 && (
        <div>
          {{data.linkColumns
            .filter(column => getInternationalizedString(column.title)) // 🚨 Only show columns with actual data
            .map((column, index) => (
            <div key={{index}}>
              {{getInternationalizedString(column.title) && (
                <h3>{{getInternationalizedString(column.title)}}</h3>
              )}}
              {{column.links && column.links.length > 0 && (
                <ul>
                  {{column.links
                    .filter(link => getInternationalizedString(link.label)) // 🚨 Only show links with actual data
                    .map((link, linkIndex) => (
                    <li key={{linkIndex}}>
                      <Link href={{getInternationalizedString(link.link?.externalUrl) || '#'}}>
                        {{getInternationalizedString(link.label)}}
                      </Link>
                    </li>
                  ))}}
                </ul>
              )}}
            </div>
          ))}}
        </div>
      )}}
      
      {{/* Copyright - ONLY if data exists from Sanity */}}
      {{data.copyrightText && getInternationalizedString(data.copyrightText) && (
        <p>{{getInternationalizedString(data.copyrightText)}}</p>
      )}}
    </footer>
  );
}}
```

// FILEPATH: page.tsx
```tsx
import {{ client }} from '@/sanity/lib/client';
import {{ get{component_name}DataQuery }} from '@/components/generated/{component_name}/query';
import {component_name} from '@/components/generated/{component_name}/component';
import {{ notFound }} from 'next/navigation';
import type {{ {component_name}Data }} from '@/components/generated/{component_name}/types';

interface PageProps {{
  params: Promise<{{ slug: string }}>;
}}

export default async function {component_name}Page({{ params }}: PageProps) {{
  const {{ slug }} = await params;
  
  const data: {component_name}Data | null = await client.fetch(get{component_name}DataQuery, {{ slug }});
  
  if (!data || !data.page) {{
    notFound();
  }}
  
  return <{component_name} data={{data}} />;
}}
```
"""

    with open(
        f"sample_ai_response_{component_name.lower()}.txt", "w", encoding="utf-8"
    ) as f:
        f.write(sample_response.strip())

    print_info(
        f"Created sample_ai_response_{component_name.lower()}.txt showing expected format"
    )


def create_schema_debug_script():
    """Create a debug script to analyze schema structure."""
    debug_script = """
const { createClient } = require('next-sanity');
require('dotenv').config({ path: '.env.local' });

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  apiVersion: '2023-03-01',
  useCdn: false,
});

async function analyzeSchema() {
  console.log('🔍 Analyzing schema structure...');
  
  try {
    // Check a sample page to understand structure
    const samplePage = await client.fetch(`*[_type == "page"][0] {
      title,
      slug,
      "titleType": title._type,
      "slugType": slug._type,
      "titleIsArray": title[0]._type,
      "slugIsArray": slug[0]._type
    }`);
    
    console.log('📄 Sample page structure:');
    console.log(JSON.stringify(samplePage, null, 2));
    
    // Determine if using internationalized arrays
    const isInternationalized = Array.isArray(samplePage?.title) && 
      samplePage.title[0]?._type?.includes('internationalized');
    
    console.log('\\n🌐 Schema type:', isInternationalized ? 'INTERNATIONALIZED ARRAYS' : 'STANDARD FIELDS');
    
    if (isInternationalized) {
      console.log('✅ Use: slug[0].value.current for filtering');
      console.log('✅ Use: getInternationalizedString() helpers in components');
      console.log('✅ Use: field { value { asset->{url, altText} } } for images');
      console.log('✅ Use: just "field" for text fields in GROQ');
    } else {
      console.log('✅ Use: slug.current for filtering');
      console.log('✅ Use: PortableText components for rich text');
    }
    
    // Test a simple query
    console.log('\\n🧪 Testing GROQ query...');
    const testQuery = isInternationalized 
      ? `*[_type == "page" && slug[0].value.current == "test"][0] { title, slug }`
      : `*[_type == "page" && slug.current == "test"][0] { title, slug }`;
    
    console.log('Test query:', testQuery);
    
  } catch (error) {
    console.error('❌ Error analyzing schema:', error);
  }
}

analyzeSchema().catch(console.error);
"""

    with open("analyze-schema.js", "w", encoding="utf-8") as f:
        f.write(debug_script.strip())

    print_info(
        "Created analyze-schema.js - run this to understand your schema structure"
    )


def create_groq_test_script():
    """Create a script to test GROQ queries."""
    test_script = """
const { createClient } = require('next-sanity');
require('dotenv').config({ path: '.env.local' });

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  apiVersion: '2023-03-01',
  useCdn: false,
});

async function testGroqQueries() {
  console.log('🧪 Testing GROQ queries for internationalized arrays...');
  
  const queries = [
    {
      name: 'Page with internationalized fields',
      query: `*[_type == "page"][0] {
        _id,
        title,
        slug,
        pageBuilder[] {
          _key,
          _type,
          _type == "herosection" => {
            headline,
            tagline,
            image { value { asset->{url, altText} } }
          }
        }
      }`
    },
    {
      name: 'Site settings',
      query: `*[_type == "siteSettings"][0] {
        siteName,
        siteDescription
      }`
    }
  ];
  
  for (const { name, query } of queries) {
    try {
      console.log(`\\n📋 Testing: ${name}`);
      console.log('Query:', query);
      const result = await client.fetch(query);
      console.log('✅ Result:', JSON.stringify(result, null, 2));
    } catch (error) {
      console.error(`❌ Error in ${name}:`, error.message);
    }
  }
}

testGroqQueries().catch(console.error);
"""

    with open("test-groq.js", "w", encoding="utf-8") as f:
        f.write(test_script.strip())

    print_info("Created test-groq.js - run this to test GROQ queries")


def setup_project_dependencies():
    """Ensure project has required dependencies and configuration."""
    print_step("Setting up project dependencies and configuration")

    # Check if required packages are installed
    package_json_path = Path("package.json")
    if package_json_path.exists():
        try:
            with open(package_json_path, "r") as f:
                package_data = json.load(f)

            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})
            all_deps = {**dependencies, **dev_dependencies}

            missing_deps = []
            required_deps = ["@portabletext/react", "@portabletext/types"]

            for dep in required_deps:
                if dep not in all_deps:
                    missing_deps.append(dep)

            if missing_deps:
                print_info(
                    f"Installing missing dependencies: {', '.join(missing_deps)}"
                )
                run_command(
                    ["npm", "install"] + missing_deps,
                    step_description="Install PortableText dependencies",
                )
            else:
                print_success("All required dependencies are already installed.")

        except Exception as e:
            print_info(f"Could not read package.json: {e}")

    # Configure next.config.ts for Sanity images
    next_config_path = Path("next.config.ts")
    if next_config_path.exists():
        try:
            with open(next_config_path, "r", encoding="utf-8") as f:
                content = f.read()

            if "cdn.sanity.io" not in content:
                print_info("Updating next.config.ts to allow Sanity CDN images...")

                # Simple regex replacement to add Sanity image config
                if "images:" in content:
                    print_info(
                        "Images config already exists, please manually add Sanity CDN domain."
                    )
                else:
                    # Add images config
                    content = content.replace(
                        "const nextConfig: NextConfig = {",
                        """const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "cdn.sanity.io",
        port: "",
        pathname: "/images/**",
      },
    ],
  },""",
                    )

                    with open(next_config_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print_success(
                        "Updated next.config.ts with Sanity CDN configuration."
                    )
            else:
                print_success("next.config.ts already configured for Sanity images.")

        except Exception as e:
            print_info(f"Could not update next.config.ts: {e}")
            print_info(
                "Please manually add Sanity CDN domain to your Next.js image configuration."
            )


def main():
    load_dotenv()
    figma_api_key = os.getenv("FIGMA_API_KEY")
    figma_file_id = os.getenv("FIGMA_FILE_KEY")

    if not figma_api_key or not figma_file_id:
        print_error("FIGMA_API_KEY and FIGMA_FILE_KEY must be set in your .env file.")

    # 0. Setup project dependencies and configuration
    setup_project_dependencies()

    # 0.5. Create schema analysis tools
    create_schema_debug_script()
    create_groq_test_script()

    # 1. Analyze all available Sanity schemas
    all_schemas = get_all_sanity_schemas_as_json()
    all_schemas_json_str = json.dumps(all_schemas, indent=2)

    # 2. User selects a Figma design to build
    figma_data = get_figma_document_data(figma_api_key, figma_file_id)
    selected_frame = select_figma_frame(figma_data)

    component_name = format_name_to_pascal_case(selected_frame["name"])
    node_id = selected_frame["id"]

    # Create sample AI response for debugging
    create_sample_ai_response(component_name)

    # 3. Export the visual blueprint
    figma_image = export_figma_frame_as_image(node_id, figma_api_key, figma_file_id)

    # 4. Generate the AI prompt and get all code artifacts
    prompt = generate_ai_prompt(all_schemas_json_str, component_name)
    ai_response = call_gemini_api(prompt, figma_image)
    if not ai_response:
        print_error("Failed to get a response from the AI. Halting.")

    # 5. Create all files, including the new page route
    component_dir = Path(f"src/components/generated/{component_name}")
    # Create a dynamic route based on the component name, e.g., /blog/[slug]
    page_route_name = re.sub(
        r"(?<!^)(?=[A-Z])", "-", component_name
    ).lower()  # BlogPost -> blog-post
    page_dir = Path(
        f"src/app/{page_route_name}s/[slug]"
    )  # -> src/app/blog-posts/[slug]

    parse_and_create_files(ai_response, component_name, component_dir, page_dir)

    print("\n🚀 Enhanced UI generation complete!")
    print(f"   - Component files are in: {component_dir}")
    print(f"   - A new page route is at: {page_dir}")
    print(
        f"   - Sample format created: sample_ai_response_{component_name.lower()}.txt"
    )
    print("\nNext Steps:")
    print(
        f"1. **Review the generated code**, especially the query in `{component_dir / 'query.ts'}` to see how the AI mapped the design to your schemas."
    )
    print(
        f"2. **Go to your Sanity Studio**, create content for the relevant schema(s), and publish."
    )
    print(
        f"3. **Start your app** (`npm run dev`) and navigate to the new route (e.g., `http://localhost:3000/{page_route_name}s/your-slug`)."
    )
    print("\n💡 **Tips**: ")
    print(f"   - Check ai_response_debug.txt if you encounter parsing issues")
    print(
        f"   - Use sample_ai_response_{component_name.lower()}.txt as a format reference"
    )
    print(f"   - Run analyze-schema.js to understand your data structure")
    print(f"   - Run test-groq.js to test GROQ queries before using them")
    print(f"   - Run create-sample-data.js to populate your dataset with test data")
    print(
        "   - The script has automatically configured your project for internationalized arrays and Sanity images!"
    )
    print(
        "\n🚨 **Important**: The generated UI components contain NO static content - everything comes from your Sanity data!"
    )
    print(
        "🌐 **Global Components**: Header and Footer are generated as separate components and included in all pages!"
    )


if __name__ == "__main__":
    main()
