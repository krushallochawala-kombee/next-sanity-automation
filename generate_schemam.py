import os
import re
import sys
import time
import json
import logging
import shutil
from typing import Dict, Any, List, Set, Optional, Union
from datetime import datetime
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from json_repair import loads as json_repair_loads
from dataclasses import dataclass, field
from pathlib import Path

# --- ⚙️ 1. ENHANCED CONFIGURATION SYSTEM ---


@dataclass
class FigmaConfig:
    """Configuration for Figma API integration"""

    api_key: str
    file_key: str
    page_name: str = "Page 1"
    main_frame_name: str = "Desktop"
    max_depth: int = 7
    timeout: int = 60


@dataclass
class AIConfig:
    """Configuration for AI model settings"""

    api_key: str
    model_name: str = "gemini-2.5-flash"
    rate_limit_delay: float = 1.2
    max_retries: int = 3


@dataclass
class LanguageConfig:
    """Configuration for internationalization"""

    id: str
    title: str


@dataclass
class I18nConfig:
    """Internationalization configuration"""

    enabled: bool = True
    supported_languages: List[LanguageConfig] = field(
        default_factory=lambda: [
            LanguageConfig("en", "English"),
            LanguageConfig("hin", "Hindi"),
        ]
    )
    default_languages: List[str] = field(default_factory=lambda: ["en"])
    field_types: List[str] = field(
        default_factory=lambda: ["string", "text", "image", "url", "file", "slug"]
    )


@dataclass
class ProjectConfig:
    """Project structure configuration"""

    schemas_dir: str = "./src/sanity/schemaTypes"
    structure_file: str = "src/sanity/structure.ts"
    config_file: str = "sanity.config.ts"
    log_dir: str = "logs"


@dataclass
class ValidationConfig:
    """Validation rules configuration"""

    max_fields_per_schema: int = 6
    built_in_types: Set[str] = field(
        default_factory=lambda: {
            "string",
            "text",
            "image",
            "file",
            "url",
            "slug",
            "number",
            "boolean",
            "array",
            "object",
            "reference",
            "block",
            "date",
            "datetime",
        }
    )
    required_global_docs: List[str] = field(
        default_factory=lambda: ["page", "siteSettings"]
    )
    required_objects: List[str] = field(default_factory=lambda: ["seo"])


@dataclass
class AppConfig:
    """Main application configuration"""

    figma: FigmaConfig
    ai: AIConfig
    i18n: I18nConfig
    project: ProjectConfig
    validation: ValidationConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables"""
        load_dotenv()

        # Required environment variables
        figma_api_key = os.getenv("FIGMA_API_KEY")
        figma_file_key = os.getenv("FIGMA_FILE_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")

        if not all([figma_api_key, figma_file_key, gemini_api_key]):
            raise ValueError("Missing required API keys in .env file")

        # Optional environment variables with defaults
        figma_config = FigmaConfig(
            api_key=figma_api_key,
            file_key=figma_file_key,
            page_name=os.getenv("FIGMA_PAGE_NAME", "Page 1"),
            main_frame_name=os.getenv("FIGMA_MAIN_FRAME_NAME", "Desktop"),
            max_depth=int(os.getenv("FIGMA_MAX_DEPTH", "7")),
            timeout=int(os.getenv("FIGMA_TIMEOUT", "60")),
        )

        ai_config = AIConfig(
            api_key=gemini_api_key,
            model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash"),
            rate_limit_delay=float(os.getenv("AI_RATE_LIMIT_DELAY", "1.2")),
            max_retries=int(os.getenv("AI_MAX_RETRIES", "3")),
        )

        # Parse languages from environment if provided
        languages_json = os.getenv("I18N_LANGUAGES")
        if languages_json:
            try:
                languages_data = json.loads(languages_json)
                supported_languages = [
                    LanguageConfig(lang["id"], lang["title"]) for lang in languages_data
                ]
            except (json.JSONDecodeError, KeyError):
                supported_languages = I18nConfig().supported_languages
        else:
            supported_languages = I18nConfig().supported_languages

        i18n_config = I18nConfig(
            enabled=os.getenv("I18N_ENABLED", "true").lower() == "true",
            supported_languages=supported_languages,
            default_languages=os.getenv("I18N_DEFAULT_LANGUAGES", "en").split(","),
            field_types=os.getenv(
                "I18N_FIELD_TYPES", "string,text,image,url,file,slug"
            ).split(","),
        )

        project_config = ProjectConfig(
            schemas_dir=os.getenv("SCHEMAS_DIR", "./src/sanity/schemaTypes"),
            structure_file=os.getenv("STRUCTURE_FILE", "src/sanity/structure.ts"),
            config_file=os.getenv("CONFIG_FILE", "sanity.config.ts"),
            log_dir=os.getenv("LOG_DIR", "logs"),
        )

        validation_config = ValidationConfig(
            max_fields_per_schema=int(os.getenv("MAX_FIELDS_PER_SCHEMA", "6")),
            built_in_types=set(
                os.getenv(
                    "BUILT_IN_TYPES",
                    "string,text,image,file,url,slug,number,boolean,array,object,reference,block,date,datetime",
                ).split(",")
            ),
            required_global_docs=os.getenv(
                "REQUIRED_GLOBAL_DOCS", "page,siteSettings"
            ).split(","),
            required_objects=os.getenv("REQUIRED_OBJECTS", "seo").split(","),
        )

        return cls(
            figma=figma_config,
            ai=ai_config,
            i18n=i18n_config,
            project=project_config,
            validation=validation_config,
        )


# --- 🛠️ 2. ENHANCED HELPER & SETUP FUNCTIONS ---


class Logger:
    """Enhanced logging system"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Configures logging to output to both console and file"""
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = log_dir / f"ai-schema-architect_{timestamp}.log"

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            logger.handlers.clear()

        # File handler
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler = logging.FileHandler(log_file_path, "w", "utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_formatter = logging.Formatter("%(asctime)s - %(message)s")
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logging.info(f"Logging configured. Detailed log saved to: {log_file_path}")


class TextProcessor:
    """Text processing utilities"""

    @staticmethod
    def to_kebab_case(text: str) -> str:
        s1 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
        return re.sub(r"[-\s]+", "-", s1).strip("-").lower()

    @staticmethod
    def to_pascal_case(text: str) -> str:
        return "".join(word.capitalize() for word in re.split(r"[\s_-]+", text))

    @staticmethod
    def to_camel_case(text: str) -> str:
        pascal = TextProcessor.to_pascal_case(text)
        return pascal[0].lower() + pascal[1:] if pascal else ""

    @staticmethod
    def extract_json_from_response(text: str) -> Optional[dict]:
        if not text:
            logging.warning("Received empty text from AI.")
            return None

        match = re.search(r"```(?:json)?\s*(\{[\s\S]+?\})\s*```", text, re.DOTALL)
        json_str = match.group(1).strip() if match else text.strip()

        try:
            return json_repair_loads(json_str)
        except Exception as e:
            logging.error(
                f"JSON repair failed: {e}\n--- AI Response Start ---\n{text}\n--- AI Response End ---"
            )
            return None


# --- 🖼️ 3. ENHANCED FIGMA DATA & SUMMARIZATION ---


class FigmaClient:
    """Enhanced Figma API client"""

    def __init__(self, config: FigmaConfig):
        self.config = config

    def get_document_data(self) -> Optional[dict]:
        """Fetch Figma document data"""
        url = f"https://api.figma.com/v1/files/{self.config.file_key}"
        headers = {"X-Figma-Token": self.config.api_key}

        try:
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            logging.info("✅ Fetched Figma file data successfully.")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching Figma file data: {e}")
            return None

    def clean_node_for_ai(self, node: dict, depth=0) -> Optional[dict]:
        """Clean and simplify Figma node data for AI processing"""
        if not node or depth > self.config.max_depth or not node.get("visible", True):
            return None

        cleaned = {"name": node.get("name", "Untitled"), "type": node.get("type")}

        if node.get("type") == "TEXT":
            cleaned["characters"] = node.get("characters")

        if any(f.get("type") == "IMAGE" for f in node.get("fills", [])):
            cleaned["isImagePlaceholder"] = True

        if "children" in node:
            children = [
                self.clean_node_for_ai(child, depth + 1)
                for child in node.get("children", [])
            ]
            cleaned_children = [c for c in children if c]
            if cleaned_children:
                cleaned["children"] = cleaned_children

        return cleaned

    def get_page_sections(self) -> List[dict]:
        """Extract sections from specified Figma page and frame"""
        logging.info(
            f"📄 Fetching sections from Figma frame '{self.config.main_frame_name}' "
            f"on page '{self.config.page_name}'..."
        )

        figma_data = self.get_document_data()
        if not figma_data:
            return []

        try:
            document = figma_data["document"]
            target_page = next(
                (
                    p
                    for p in document["children"]
                    if p.get("name") == self.config.page_name
                ),
                None,
            )
            if not target_page:
                raise ValueError(f"Page '{self.config.page_name}' not found.")

            main_frame = next(
                (
                    f
                    for f in target_page["children"]
                    if f.get("type") == "FRAME"
                    and f.get("name") == self.config.main_frame_name
                ),
                None,
            )
            if not main_frame:
                raise ValueError(
                    f"Main frame '{self.config.main_frame_name}' not found."
                )

            sections = [
                {"name": n.get("name"), "node": n}
                for n in main_frame["children"]
                if n.get("type") in ["FRAME", "COMPONENT", "INSTANCE"] and n.get("name")
            ]

            if not sections:
                raise ValueError(
                    f"No named sections found in '{self.config.main_frame_name}'."
                )

            logging.info(f"✅ Found {len(sections)} top-level page sections.")
            return sections

        except (ValueError, KeyError, StopIteration) as e:
            logging.error(f"❌ Figma Error: {e}")
            return []


# --- 🤖 4. ENHANCED AI ARCHITECT ---


class PromptGenerator:
    """Dynamic prompt generation system"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.text_processor = TextProcessor()

    def generate_phase_one_prompt(self, sections_summary: List[dict]) -> str:
        """Generate architectural planning prompt"""
        return f"""
You are a top-tier Sanity.io Lead Architect. Analyze the lightweight JSON representation of a Figma design and create a high-level, scalable, and DRY schema plan.

**Architectural Rules:**
1. **Documents vs. Objects:** `documents` are for queryable data collections (e.g., `post`, `page`, `siteSettings`, `header`, `footer`). `objects` are for structural components used on pages (e.g., `heroSection`, `ctaButton`, `seo`).
2. **Global Documents Rule:** `siteSettings`, `header`, and `footer` are global documents that will be created as separate documents for site-wide content.
3. **Header and Footer Rule (CRITICAL):** If you see 'Header' or 'Footer' sections in the Figma design, they MUST be created as `documents` (not objects).
4. **SEO Rule (CRITICAL):** Always create an `seo` object that can be embedded in page-type documents. This object should contain meta title, meta description, og:image, and other SEO fields.
5. **The Grid Rule:** When you see a "structure" with repeating children of the same name (e.g., a "Team" section with multiple "Team Member" children), define a `document` for the underlying data (e.g., `teamMember`) and an `object` for the page section (e.g., `teamSection`) that will hold an array of `references` to those documents.
6. **Global Content Rule:** Always plan a `siteSettings` document. If header or footer sections are detected, create separate `header` and `footer` documents.
7. **CRITICAL NAMING:** All names in your output MUST be in EXACT camelCase format (e.g., "metricsSection", "companyLogo", "heroSection", "header", "footer", "seo").
8. **Always include a `page` document and an `seo` object.**

**Figma JSON Structure:**
{json.dumps(sections_summary, indent=2)}

**Your Output:**
Return ONLY a valid JSON object with `documents` and `objects` keys. The values for these keys must be arrays of camelCase schema names. Do not include a 'blocks' key.

**Remember: Header and Footer MUST be documents if they exist in the design.**
"""

    def generate_phase_two_prompt(
        self, schema_name: str, classification: str, plan: dict, structure_info: str
    ) -> str:
        """Generate schema code generation prompt"""
        all_objects = plan.get("objects", [])
        all_documents = plan.get("documents", [])
        page_builder_objects = [
            obj
            for obj in all_objects
            if obj not in ["siteSettings", "header", "footer"]
        ]

        special_instructions = self._get_special_instructions(
            schema_name, page_builder_objects
        )

        i18n_types = (
            ", ".join(
                [
                    f"`internationalizedArray{t.title()}`"
                    for t in self.config.i18n.field_types
                ]
            )
            if self.config.i18n.enabled
            else "standard Sanity types"
        )

        # Enhanced preview instructions
        preview_instructions = self._get_preview_instructions(
            schema_name, classification
        )

        return f"""
You are an expert Sanity.io schema generator. Your most important task is to create CONCISE and FOCUSED TypeScript schema code.

### **CRITICAL: SCHEMA TYPE REQUIREMENT**
This schema MUST be of type: **'{classification}'**
Set the 'type' property in your defineType call to exactly: '{classification}'

### **CRITICAL: MINIMAL FIELD APPROACH**
- **Create ONLY essential content fields** - avoid over-engineering
- **Focus on actual content**, not visual styling or layout elements
- **Maximum {self.config.validation.max_fields_per_schema} fields per schema** unless absolutely necessary
- **Combine related fields** rather than creating separate ones for each visual element

### **Rule 1: Use `defineType` and `defineField`**
You MUST use the standard `defineType` and `defineField` functions imported from `sanity`.
`import {{defineType, defineField}} from 'sanity'`

### **Rule 2: Correct Validation Syntax (CRITICAL)**
For validation functions, **DO NOT** add an explicit type to the `Rule` parameter:
- **Correct:** `validation: (Rule) => Rule.required()`
- **INCORRECT:** `validation: (Rule: Rule) => Rule.required()`

### **Rule 3: Array Items - NO defineType Inside Arrays (CRITICAL)**
When defining array items in the `of` property, use plain object literals, NOT defineType:
- **Correct:** `of: [{{ name: 'item', type: 'object', fields: [...] }}]`
- **INCORRECT:** `of: [defineType({{ name: 'item', type: 'object', fields: [...] }})]`

### **Rule 3b: Array Type References - Always Use 'type:' Property (CRITICAL)**
When referencing other schemas in arrays, always include the 'type:' property:
- **Correct:** `of: [{{type: 'navigationitem'}}]`
- **INCORRECT:** `of: [{{'navigationitem'}}]`

### **Rule 3c: NO Mixed Primitive/Object Types in Arrays (CRITICAL SANITY RULE)**
NEVER mix primitive types (url, string, number) with object types (reference, object) in the same array:
- **INCORRECT:** `of: [{{type: 'url'}}, {{type: 'reference'}}]` ❌ WILL BREAK SANITY
- **Correct:** `of: [{{type: 'object', fields: [{{name: 'url', type: 'url'}}]}}, {{type: 'reference'}}]`

### **Rule 4: Internationalization Types**
{"Use internationalization types for user-facing content: " + i18n_types if self.config.i18n.enabled else "Use standard Sanity types for content"}

### **Rule 5: Use Exact camelCase for Type References**
When referencing other schemas, use the exact camelCase names provided.
- **Available Documents for References:** {all_documents}
- **Available Objects for Embedding:** {all_objects}

{preview_instructions}

---
**Your Task:**
Generate a MINIMAL, focused TypeScript schema for **`{schema_name}`** of type **'{classification}'** with ONLY essential content fields.

**Figma Structure to Analyze:**
```json
{structure_info}
```
{special_instructions}

**REMEMBER: The schema type MUST be '{classification}'. Focus on the CONTENT, not the visual design. Keep it simple and essential. ALWAYS include a proper preview configuration.**

Output ONLY the raw TypeScript code. Do not wrap it in markdown backticks or add any explanation.
"""

    def _get_preview_instructions(self, schema_name: str, classification: str) -> str:
        """Generate comprehensive preview instructions"""
        is_singleton = schema_name in ["siteSettings", "header", "footer"]

        if self.config.i18n.enabled:
            preview_example = """
**Example preview for i18n fields:**
```typescript
preview: {
  select: {
    title: 'title.0.value',           // For internationalizedArrayString
    subtitle: 'description.0.value',  // For internationalizedArrayText
    media: 'image.0.value.asset',     // For internationalizedArrayImage
  },
  prepare({title, subtitle, media}) {
    return {
      title: title || 'Untitled',
      subtitle: subtitle,
      media: media,
    }
  },
}
```"""
        else:
            preview_example = """
**Example preview for standard fields:**
```typescript
preview: {
  select: {
    title: 'title',        // For string fields
    subtitle: 'description', // For text fields
    media: 'image.asset',    // For image fields
  },
  prepare({title, subtitle, media}) {
    return {
      title: title || 'Untitled',
      subtitle: subtitle,
      media: media,
    }
  },
}
```"""

        singleton_note = ""
        if is_singleton:
            singleton_note = f"""
**SINGLETON DOCUMENT NOTE:** This is a singleton document ('{schema_name}'). The preview is crucial for identifying this global content in the Studio interface. Use descriptive titles like 'Site Settings', 'Global Header', or 'Global Footer' in the prepare function."""

        return f"""
### **Rule 6: MANDATORY Preview Configuration (CRITICAL)**
**EVERY schema MUST include a comprehensive preview object.** This is essential for Sanity Studio's content management interface.

**Preview Requirements:**
1. **Always include a `preview` object** with `select` and `prepare` properties
2. **Select meaningful fields** for title, subtitle, and media when available
3. **Handle empty/undefined values** gracefully in prepare function
4. **Use appropriate field paths** based on internationalization settings
5. **Provide fallback values** for better user experience

{singleton_note}

**Field Path Rules:**
{"- **Internationalized fields:** Use `.0.value` path (e.g., `title.0.value`)" if self.config.i18n.enabled else "- **Standard fields:** Use direct field names (e.g., `title`)"}
{"- **Internationalized images:** Use `.0.value.asset` path (e.g., `image.0.value.asset`)" if self.config.i18n.enabled else "- **Standard images:** Use `.asset` path (e.g., `image.asset`)"}
- **References:** Select fields from referenced documents when needed
- **Arrays:** Consider selecting first item or count for display

**Common Preview Patterns:**
- **Title + Subtitle:** Most content schemas
- **Title + Media:** Visual content schemas  
- **Title + Description:** Text-heavy schemas
- **Custom Labels:** For singletons and special schemas

{preview_example}

**Fallback Strategies:**
- Use schema name as fallback title for singletons
- Show field count for array-heavy schemas
- Display "Draft" or "Unpublished" states when relevant
- Handle missing media gracefully"""

    def _get_special_instructions(
        self, schema_name: str, page_builder_objects: List[str]
    ) -> str:
        """Generate special instructions based on schema name"""
        special_instructions = ""

        if schema_name == "page":
            special_instructions = f"""**SPECIAL INSTRUCTION FOR 'page':** This document MUST contain: 1) A `pageBuilder` field of type `array` with `of` property referencing page sections: {page_builder_objects}, AND 2) An `seo` field of type `seo` object for SEO metadata.

**PREVIEW FOR PAGE:** Use the page title and SEO image if available. Show page slug or URL in subtitle."""
        elif schema_name == "siteSettings":
            special_instructions = f"""**SPECIAL INSTRUCTION FOR 'siteSettings':** This is a global site settings document. This document must contain a `header` field of type `reference` to `header` document, and a `footer` field of type `reference` to `footer` document.

**PREVIEW FOR SITE SETTINGS:** Always show "Site Settings" as title. Use site name or description as subtitle if available."""
        elif schema_name == "header":
            special_instructions = f"""**SPECIAL INSTRUCTION FOR 'header':** This is a global header document. Include essential header content like logo, navigation links, and any header-specific content.

**PREVIEW FOR HEADER:** Always show "Global Header" as title. Use logo or main navigation info as preview."""
        elif schema_name == "footer":
            special_instructions = f"""**SPECIAL INSTRUCTION FOR 'footer':** This is a global footer document. Include essential footer content like links, social media, copyright, and any footer-specific content.

**PREVIEW FOR FOOTER:** Always show "Global Footer" as title. Use copyright text or link count as subtitle."""
        elif schema_name == "seo":
            if self.config.i18n.enabled:
                special_instructions = f"""**SPECIAL INSTRUCTION FOR 'seo':** This is an SEO object schema that contains ALL essential SEO fields: `metaTitle` (internationalizedArrayString, max 60 chars), `metaDescription` (internationalizedArrayText, max 160 chars), `ogImage` (internationalizedArrayImage), `ogTitle` (internationalizedArrayString), `ogDescription` (internationalizedArrayText), `keywords` (array of internationalizedArrayString), `noIndex` (boolean), and `canonicalUrl` (internationalizedArrayUrl). Include proper validation rules for character limits.

**PREVIEW FOR SEO:** Use metaTitle as title, metaDescription as subtitle, and ogImage as media."""
            else:
                special_instructions = f"""**SPECIAL INSTRUCTION FOR 'seo':** This is an SEO object schema that contains ALL essential SEO fields: `metaTitle` (string, max 60 chars), `metaDescription` (text, max 160 chars), `ogImage` (image), `ogTitle` (string), `ogDescription` (text), `keywords` (array of strings), `noIndex` (boolean), and `canonicalUrl` (url). Include proper validation rules for character limits.

**PREVIEW FOR SEO:** Use metaTitle as title, metaDescription as subtitle, and ogImage as media."""

        # Add preview instruction for any other schema
        if not special_instructions:
            if schema_name.endswith("Section"):
                special_instructions = f"""**PREVIEW FOR SECTION SCHEMA:** Use the main title/heading field as title. If there's an image, use it as media. Show section type or description as subtitle."""
            else:
                special_instructions = f"""**PREVIEW FOR '{schema_name.upper()}':** Choose the most meaningful content field as title. Use images for media when available. Show secondary content as subtitle."""

        return special_instructions


class AIArchitect:
    """Enhanced AI-powered schema architect"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.text_processor = TextProcessor()
        self.prompt_generator = PromptGenerator(config)
        self.model = self._initialize_model()

    def _initialize_model(self):
        """Initialize the AI model"""
        genai.configure(api_key=self.config.ai.api_key)
        return genai.GenerativeModel(self.config.ai.model_name)

    def phase_one_architect_plan(self, sections: List[dict]) -> Optional[dict]:
        """Create architectural plan from Figma sections"""
        logging.info("🤖 PHASE 1: Creating architectural plan from Figma JSON...")

        figma_client = FigmaClient(self.config.figma)
        sections_summary = [
            {
                "name": section["name"],
                "structure": figma_client.clean_node_for_ai(section["node"]),
            }
            for section in sections
        ]

        prompt = self.prompt_generator.generate_phase_one_prompt(sections_summary)

        logging.debug(
            f"\n--- PHASE 1: PROMPT SENT TO AI ---\n{prompt}\n---------------------------------"
        )

        try:
            response = self.model.generate_content(prompt)
            logging.debug(
                f"\n--- PHASE 1: RAW AI RESPONSE ---\n{response.text}\n------------------------------"
            )

            plan = self.text_processor.extract_json_from_response(response.text)
            if not plan:
                raise ValueError("Phase 1 response did not contain valid JSON.")

            # Process and validate the plan
            plan = self._process_architectural_plan(plan, sections)

            logging.info(f"✅ PHASE 1: Architectural plan received.")
            logging.debug(f"Plan details: {json.dumps(plan, indent=2)}")
            return plan

        except Exception as e:
            logging.error(f"❌ AI Error during Phase 1: {e}", exc_info=True)
            return None

    def _process_architectural_plan(self, plan: dict, sections: List[dict]) -> dict:
        """Process and validate the architectural plan"""
        # Ensure all keys exist and normalize names to proper camelCase
        for category in ["documents", "objects"]:
            plan.setdefault(category, [])
            plan[category] = sorted(
                list(
                    set(
                        [
                            self.text_processor.to_camel_case(name)
                            for name in plan[category]
                        ]
                    )
                )
            )

        # Deduplicate siteSettings variants
        sitesettings_variants = [
            "siteSettings",
            "siteConfig",
            "globalSettings",
            "settings",
        ]
        sitesettings_found = [
            name
            for name in plan["documents"]
            if any(variant.lower() == name.lower() for variant in sitesettings_variants)
        ]
        if sitesettings_found:
            for variant in sitesettings_found:
                if variant in plan["documents"]:
                    plan["documents"].remove(variant)
            plan["documents"].append("siteSettings")

        # Ensure essential documents and objects exist
        for doc in self.config.validation.required_global_docs:
            if doc not in plan["documents"]:
                plan["documents"].append(doc)

        for obj in self.config.validation.required_objects:
            if obj not in plan["objects"]:
                plan["objects"].append(obj)

        # Check if header/footer sections exist in Figma
        section_names = [
            self.text_processor.to_camel_case(section["name"]) for section in sections
        ]
        for section_name in section_names:
            if "header" in section_name.lower():
                if "header" not in plan["documents"]:
                    plan["documents"].append("header")
                if "header" in plan["objects"]:
                    plan["objects"].remove("header")
            elif "footer" in section_name.lower():
                if "footer" not in plan["documents"]:
                    plan["documents"].append("footer")
                if "footer" in plan["objects"]:
                    plan["objects"].remove("footer")

        # Sort final lists
        plan["documents"].sort()
        plan["objects"].sort()

        return plan

    def phase_two_generate_schema_code(
        self, schema_name: str, classification: str, plan: dict, sections: List[dict]
    ) -> Optional[str]:
        """Generate TypeScript schema code for a specific schema"""
        logging.info(
            f"  🤖 PHASE 2: Generating TypeScript code for '{schema_name}' ({classification})..."
        )

        figma_client = FigmaClient(self.config.figma)
        relevant_section_json = next(
            (
                figma_client.clean_node_for_ai(s["node"])
                for s in sections
                if self.text_processor.to_camel_case(s["name"]) == schema_name
            ),
            None,
        )

        structure_info = (
            json.dumps(relevant_section_json, indent=2)
            if relevant_section_json
            else "No specific Figma structure found for this schema. Please generate a logical schema based on its name and classification."
        )

        prompt = self.prompt_generator.generate_phase_two_prompt(
            schema_name, classification, plan, structure_info
        )

        logging.debug(
            f"\n--- PHASE 2: PROMPT SENT TO AI for '{schema_name}' ---\n{prompt}\n----------------------------------"
        )

        try:
            time.sleep(self.config.ai.rate_limit_delay)
            response = self.model.generate_content(prompt)
            logging.debug(
                f"\n--- PHASE 2: RAW AI RESPONSE for '{schema_name}' ---\n{response.text}\n------------------------------"
            )

            if response.text:
                logging.info(f" ✅ TypeScript code for '{schema_name}' generated.")
                return response.text
            raise ValueError("AI returned an empty response.")

        except Exception as e:
            logging.error(
                f"❌ AI Error during Phase 2 for '{schema_name}': {e}", exc_info=True
            )
            return None


# --- 📜 5. ENHANCED SANITY FILE GENERATOR & CORRECTION ---


class CodeCorrector:
    """Enhanced code correction system"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.text_processor = TextProcessor()

    def correct_generated_code(
        self, code: str, all_valid_names: Set[str], expected_type: str = None
    ) -> str:
        """Apply comprehensive corrections to AI-generated code"""
        original_code = code
        corrections_applied = []

        # Apply all correction methods
        code = self._remove_markdown_formatting(code, corrections_applied)
        code = self._fix_schema_type(code, expected_type, corrections_applied)
        code = self._fix_validation_syntax(code, corrections_applied)
        code = self._fix_define_type_in_arrays(code, corrections_applied)
        code = self._fix_missing_type_property(code, corrections_applied)
        code = self._fix_i18n_fields_property(code, corrections_applied)
        code = self._fix_i18n_of_property(code, corrections_applied)
        code = self._fix_type_name_casing(code, all_valid_names, corrections_applied)
        code = self._ensure_imports(code, corrections_applied)
        code = self._fix_invalid_i18n_types(code, corrections_applied)
        code = self._simplify_verbose_names(code, corrections_applied)
        code = self._fix_mixed_array_types(code, corrections_applied)
        code = self._add_missing_preview(code, expected_type, corrections_applied)

        # Log corrections
        if corrections_applied:
            logging.info(
                f"    🔧 Auto-corrections applied: {' | '.join(corrections_applied)}"
            )

        return code

    def _remove_markdown_formatting(self, code: str, corrections: List[str]) -> str:
        """Remove markdown formatting from generated code"""
        if code.startswith("```") or code.endswith("```"):
            code = re.sub(
                r"^```(?:typescript|javascript|ts|js)?\s*", "", code, flags=re.MULTILINE
            )
            code = re.sub(r"\s*```\s*$", "", code, flags=re.MULTILINE)
            corrections.append("removed markdown formatting")

        if re.search(r";```\w*", code):
            code = re.sub(r";```\w*\s*", "", code)
            corrections.append("removed stray markdown syntax")

        return code

    def _fix_schema_type(
        self, code: str, expected_type: str, corrections: List[str]
    ) -> str:
        """Fix incorrect schema type declarations"""
        if expected_type:
            type_pattern = r"type:\s*['\"]([^'\"]+)['\"]"
            type_match = re.search(type_pattern, code)
            if type_match:
                current_type = type_match.group(1)
                if current_type != expected_type:
                    code = re.sub(type_pattern, f"type: '{expected_type}'", code)
                    corrections.append(
                        f"schema type: '{current_type}' → '{expected_type}'"
                    )
        return code

    def _fix_validation_syntax(self, code: str, corrections: List[str]) -> str:
        """Fix validation function typing"""
        validation_pattern = r"\(Rule:\s*[A-Za-z_][A-Za-z0-9_]*\)"
        if re.search(validation_pattern, code):
            code = re.sub(validation_pattern, r"(Rule)", code)
            corrections.append("validation function syntax (Rule: Rule) → (Rule)")
        return code

    def _fix_define_type_in_arrays(self, code: str, corrections: List[str]) -> str:
        """Fix defineType usage inside array 'of' properties"""
        defineType_in_array_pattern = r"of:\s*\[\s*defineType\s*\(\s*\{"
        if re.search(defineType_in_array_pattern, code):
            code = re.sub(r"of:\s*\[\s*defineType\s*\(\s*\{", "of: [{", code)
            code = re.sub(r"\}\s*\)\s*,?\s*\]", "}]", code)
            corrections.append("defineType inside arrays → plain objects")
        return code

    def _fix_missing_type_property(self, code: str, corrections: List[str]) -> str:
        """Fix missing 'type:' property in array items"""
        missing_type_pattern = r"of:\s*\[\s*\{\s*['\"]([^'\"]+)['\"]\s*\}\s*\]"
        if re.search(missing_type_pattern, code):
            code = re.sub(missing_type_pattern, r"of: [{type: '\1'}]", code)
            corrections.append("added missing 'type:' property in array items")
        return code

    def _fix_i18n_fields_property(self, code: str, corrections: List[str]) -> str:
        """Remove 'fields' property from internationalized array types"""
        i18n_image_fields_pattern = r"(type:\s*['\"]internationalizedArray(Image|File)['\"][^}]*?),\s*fields:\s*\[[^\]]*?\]"
        if re.search(i18n_image_fields_pattern, code, re.DOTALL):
            code = re.sub(i18n_image_fields_pattern, r"\1", code, flags=re.DOTALL)
            corrections.append("removed 'fields' from internationalizedArray type")
        return code

    def _fix_i18n_of_property(self, code: str, corrections: List[str]) -> str:
        """Remove 'of' property from internationalized array types"""
        i18n_array_of_pattern = r"(type:\s*['\"]internationalizedArray(?:Text|String|Url|Slug)['\"][^}]*?),\s*of:\s*\[[^\]]*?\]"
        if re.search(i18n_array_of_pattern, code, re.DOTALL):
            code = re.sub(i18n_array_of_pattern, r"\1", code, flags=re.DOTALL)
            corrections.append("removed 'of' from internationalizedArray type")
        return code

    def _fix_type_name_casing(
        self, code: str, all_valid_names: Set[str], corrections: List[str]
    ) -> str:
        """Fix type name casing issues"""
        name_map = {name.lower(): name for name in all_valid_names}
        type_corrections = []

        def replace_type_reference(match):
            quote_char = match.group(1)
            type_name = match.group(2)

            if (
                type_name in self.config.validation.built_in_types
                or "internationalizedArray" in type_name
            ):
                return match.group(0)

            type_name_lower = type_name.lower()
            if type_name_lower in name_map:
                correct_name = name_map[type_name_lower]
                if type_name != correct_name:
                    type_corrections.append(f"'{type_name}' → '{correct_name}'")
                    return f"{quote_char}{correct_name}{quote_char}"
            return match.group(0)

        type_pattern = r"type:\s*(['\"])([^'\"]+)\1"
        code = re.sub(type_pattern, replace_type_reference, code)

        if type_corrections:
            corrections.append(
                f"type name casing: {', '.join(sorted(list(set(type_corrections))))}"
            )

        return code

    def _ensure_imports(self, code: str, corrections: List[str]) -> str:
        """Ensure required imports are present"""
        if "defineType" not in code and "defineField" not in code:
            if "name:" in code and "title:" in code and "type:" in code:
                code = f"import {{defineType, defineField}} from 'sanity'\n\n{code}"
                corrections.append("added missing defineType/defineField import")
        return code

    def _fix_invalid_i18n_types(self, code: str, corrections: List[str]) -> str:
        """Fix invalid internationalized array type names"""
        invalid_i18n_types = {
            "internationalizedArrayOfPortableText": "internationalizedArrayText",
            "internationalizedArrayPortableText": "internationalizedArrayText",
            "internationalizedArrayRichText": "internationalizedArrayText",
            "internationalizedArrayBlock": "internationalizedArrayText",
            "internationalizedArrayContent": "internationalizedArrayText",
            "internationalizedArrayArray": "internationalizedArrayText",
            "internationalizedArrayReference": "reference",
            "internationalizedArrayCrossDatasetReference": "crossDatasetReference",
            "internationalizedArrayDocument": "reference",
        }

        fixed_types = []
        for incorrect_name, correct_name in invalid_i18n_types.items():
            if incorrect_name in code:
                code = code.replace(incorrect_name, correct_name)
                fixed_types.append(f"{incorrect_name} → {correct_name}")

        if fixed_types:
            corrections.append(
                f"corrected invalid i18n types: {', '.join(fixed_types[:2])}{'...' if len(fixed_types) > 2 else ''}"
            )

        return code

    def _simplify_verbose_names(self, code: str, corrections: List[str]) -> str:
        """Simplify verbose field names"""
        verbose_replacements = {
            r"name:\s*['\"]primaryTitle['\"]": "name: 'title'",
            r"name:\s*['\"]mainTitle['\"]": "name: 'title'",
            r"name:\s*['\"]headerTitle['\"]": "name: 'title'",
            r"name:\s*['\"]sectionTitle['\"]": "name: 'title'",
            r"name:\s*['\"]primaryDescription['\"]": "name: 'description'",
            r"name:\s*['\"]mainDescription['\"]": "name: 'description'",
            r"name:\s*['\"]sectionDescription['\"]": "name: 'description'",
            r"name:\s*['\"]primaryText['\"]": "name: 'text'",
            r"name:\s*['\"]mainText['\"]": "name: 'text'",
            r"name:\s*['\"]heroImage['\"]": "name: 'image'",
            r"name:\s*['\"]mainImage['\"]": "name: 'image'",
            r"name:\s*['\"]primaryImage['\"]": "name: 'image'",
            r"name:\s*['\"]featuredImage['\"]": "name: 'image'",
        }

        simplified_names = []
        for pattern, replacement in verbose_replacements.items():
            if re.search(pattern, code, re.IGNORECASE):
                code = re.sub(pattern, replacement, code, flags=re.IGNORECASE)
                simplified_names.append(pattern.split("'")[1])

        if simplified_names:
            corrections.append(
                f"simplified verbose field names: {', '.join(simplified_names[:3])}{'...' if len(simplified_names) > 3 else ''}"
            )

        return code

    def _fix_mixed_array_types(self, code: str, corrections: List[str]) -> str:
        """Fix mixed primitive/object types in arrays"""
        mixed_array_pattern = r'of:\s*\[\s*\{[^}]*type:\s*[\'"]url[\'"][^}]*\}[^}]*\{[^}]*type:\s*[\'"]reference[\'"]'
        if re.search(mixed_array_pattern, code, re.DOTALL):
            url_object_fix = r'(\s*\{\s*type:\s*[\'"])url([\'"][^}]*name:\s*[\'"]([^\'\"]+)[\'"][^}]*title:\s*[\'"]([^\'\"]+)[\'"][^}]*)\},'
            code = re.sub(
                url_object_fix,
                r'\1object\2fields: [defineField({name: "url", title: "URL", type: "url", validation: (Rule) => Rule.required()})],},',
                code,
                flags=re.DOTALL,
            )
            corrections.append("fixed mixed primitive/object types in arrays")

        return code

    def _add_missing_preview(self, code: str, expected_type: str, corrections: List[str]) -> str:
        """Add missing preview configuration if it's a singleton document."""
        if expected_type in ["siteSettings", "header", "footer"]:
            preview_pattern = r"preview:\s*\{"
            if not re.search(preview_pattern, code):
                corrections.append("added missing preview configuration for singleton")
                return f"preview: {{\n  select: {{\n    title: 'Untitled',\n    subtitle: 'Untitled',\n    media: null,\n  }},\n  prepare: (selection) => {{\n    return {{\n      title: selection.title || 'Untitled',\n      subtitle: selection.subtitle || 'Untitled',\n      media: selection.media || null,\n    }};\n  }},\n}}"
        return code


class CodeValidator:
    """Enhanced code validation system"""

    def __init__(self, config: AppConfig):
        self.config = config

    def validate_generated_code(self, code: str, schema_name: str) -> List[str]:
        """Validate generated code and return list of issues"""
        issues = []

        # Apply all validation checks
        issues.extend(self._check_markdown_formatting(code))
        issues.extend(self._check_define_type_in_arrays(code))
        issues.extend(self._check_missing_type_property(code))
        issues.extend(self._check_i18n_fields_property(code))
        issues.extend(self._check_i18n_of_property(code))
        issues.extend(self._check_invalid_i18n_types(code))
        issues.extend(self._check_validation_syntax(code))
        issues.extend(self._check_missing_imports(code))
        issues.extend(self._check_camel_case_violations(code))
        issues.extend(self._check_field_count(code))
        issues.extend(self._check_verbose_field_names(code))
        issues.extend(self._check_mixed_array_types(code))
        issues.extend(self._check_missing_preview(code, schema_name))

        if issues:
            logging.warning(f"  ⚠️  Validation issues found in '{schema_name}':")
            for issue in issues:
                logging.warning(f"     {issue}")

        return issues

    def _check_markdown_formatting(self, code: str) -> List[str]:
        """Check for markdown formatting in TypeScript code"""
        if re.search(r"```\w*", code) or code.startswith("```") or code.endswith("```"):
            return ["❌ Found markdown formatting in TypeScript code"]
        return []

    def _check_define_type_in_arrays(self, code: str) -> List[str]:
        """Check for defineType inside arrays"""
        if re.search(r"of:\s*\[\s*defineType\s*\(", code):
            return ["❌ Found defineType inside array 'of' property"]
        return []

    def _check_missing_type_property(self, code: str) -> List[str]:
        """Check for missing 'type:' property in array items"""
        if re.search(r"of:\s*\[\s*\{\s*['\"][^'\"]+['\"]\s*\}", code):
            return ["❌ Found missing 'type:' property in array items"]
        return []

    def _check_i18n_fields_property(self, code: str) -> List[str]:
        """Check for fields property on i18n image types"""
        if re.search(
            r"type:\s*['\"]internationalizedArray(Image|File)['\"].*?fields:\s*\[",
            code,
            re.DOTALL,
        ):
            return ["❌ Found 'fields' property on internationalizedArray type"]
        return []

    def _check_i18n_of_property(self, code: str) -> List[str]:
        """Check for 'of' property on i18n text/array types"""
        if re.search(
            r"type:\s*['\"]internationalizedArray(?:Text|String|Url|Slug)['\"].*?of:\s*\[",
            code,
            re.DOTALL,
        ):
            return ["❌ Found 'of' property on internationalizedArray type"]
        return []

    def _check_invalid_i18n_types(self, code: str) -> List[str]:
        """Check for invalid internationalized array type names"""
        issues = []

        invalid_i18n_pattern = r"type:\s*['\"]internationalizedArray(?:OfPortableText|PortableText|RichText|Block|Content|Array|Of\w+)['\"]"
        if re.search(invalid_i18n_pattern, code):
            issues.append(
                "❌ Found invalid internationalizedArray type (only String, Text, Image, File, Url, Slug are available)"
            )

        invalid_ref_pattern = r"type:\s*['\"]internationalizedArray(?:Reference|CrossDatasetReference|Document)['\"]"
        if re.search(invalid_ref_pattern, code):
            issues.append(
                "❌ Found invalid internationalizedArray reference type (use 'reference' instead)"
            )

        return issues

    def _check_validation_syntax(self, code: str) -> List[str]:
        """Check for explicit typing in validation functions"""
        if re.search(r"\(Rule:\s*[A-Za-z]", code):
            return ["❌ Found explicit typing in validation function parameter"]
        return []

    def _check_missing_imports(self, code: str) -> List[str]:
        """Check for missing imports"""
        if ("defineType" in code or "defineField" in code) and not re.search(
            r"import.*defineType.*from.*sanity", code
        ):
            return ["⚠️  Missing import for defineType/defineField"]
        return []

    def _check_camel_case_violations(self, code: str) -> List[str]:
        """Check for camelCase violations in type references"""
        issues = []
        type_references = re.findall(r"type:\s*['\"]([^'\"]+)['\"]", code)

        for type_ref in type_references:
            if (
                type_ref[0].isupper()
                and "internationalizedArray" not in type_ref
                and type_ref not in self.config.validation.built_in_types
            ):
                issues.append(f"⚠️  Type reference '{type_ref}' should be camelCase")

        return issues

    def _check_field_count(self, code: str) -> List[str]:
        """Check for schemas with too many fields"""
        field_count = len(re.findall(r"defineField\s*\(", code))
        if field_count > self.config.validation.max_fields_per_schema:
            return [
                f"⚠️  Schema has {field_count} fields - consider simplifying (recommended: {self.config.validation.max_fields_per_schema} fields max)"
            ]
        return []

    def _check_verbose_field_names(self, code: str) -> List[str]:
        """Check for verbose field names"""
        verbose_patterns = [
            r'name:\s*[\'"][a-z]*Title[A-Z][a-z]*[\'"]',
            r'name:\s*[\'"][a-z]*Description[A-Z][a-z]*[\'"]',
            r'name:\s*[\'"][a-z]*Text[A-Z][a-z]*[\'"]',
            r'name:\s*[\'"][a-z]*Image[A-Z][a-z]*[\'"]',
        ]

        for pattern in verbose_patterns:
            if re.search(pattern, code):
                return [
                    "⚠️  Found verbose field names - consider simpler naming (e.g., 'title', 'description', 'image')"
                ]

        return []

    def _check_mixed_array_types(self, code: str) -> List[str]:
        """Check for mixed primitive/object types in arrays"""
        mixed_array_pattern = r'of:\s*\[\s*\{[^}]*type:\s*[\'"](?:url|string|number|boolean)[\'"][^}]*\}[^}]*\{[^}]*type:\s*[\'"](?:reference|object)[\'"]'
        if re.search(mixed_array_pattern, code, re.DOTALL):
            return [
                "❌ Found mixed primitive/object types in array - will break Sanity Studio"
            ]
        return []

    def _check_missing_preview(self, code: str, schema_name: str) -> List[str]:
        """Check for missing preview configuration"""
        if "preview:" not in code:
            return [
                f"⚠️  Missing preview configuration for '{schema_name}'. Every schema MUST include a preview object."
            ]
        return []


# --- 📁 6. ENHANCED FILE GENERATION SYSTEM ---


class TemplateGenerator:
    """Dynamic template generation system"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.text_processor = TextProcessor()

    def generate_structure_template(self, plan: dict) -> str:
        """Generate structure.ts template"""
        documents = plan.get("documents", [])
        global_docs = [
            doc for doc in documents if doc in ["siteSettings", "header", "footer"]
        ]
        regular_docs = [
            doc for doc in documents if doc not in ["siteSettings", "header", "footer"]
        ]

        global_items = []
        for doc in global_docs:
            title = self._format_document_title(doc)
            global_items.append(
                f"""    S.listItem()
      .title('{title}')
      .id('{doc}')
      .child(
        S.document()
          .schemaType('{doc}')
          .documentId('{doc}')
      ),"""
            )

        regular_items = []
        for doc in regular_docs:
            title = self._format_document_title(doc)
            regular_items.append(
                f"""    S.documentTypeListItem('{doc}').title('{title}'),"""
            )

        return f"""import {{ StructureResolver }} from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('Content')
    .items([
      // Global Documents
{chr(10).join(global_items)}
      
      // Divider
      S.divider(),
      
      // Regular Documents
{chr(10).join(regular_items)}
    ])
"""

    def _format_document_title(self, doc: str) -> str:
        """Format document name for display"""
        if doc == "siteSettings":
            return "Site Settings"
        elif doc == "header":
            return "Header"
        elif doc == "footer":
            return "Footer"
        else:
            return doc.replace("Settings", " Settings").title()

    def generate_sanity_config_template(self) -> str:
        """Generate sanity.config.ts template"""
        if not self.config.i18n.enabled:
            return self._generate_basic_config_template()

        languages_config = ",\n  ".join(
            [
                f"{{id: '{lang.id}', title: '{lang.title}'}}"
                for lang in self.config.i18n.supported_languages
            ]
        )

        field_types_config = ", ".join(
            [f"'{ft}'" for ft in self.config.i18n.field_types]
        )
        default_languages_config = ", ".join(
            [f"'{lang}'" for lang in self.config.i18n.default_languages]
        )

        return f"""'use client'

/**
 * This configuration is used to for the Sanity Studio that's mounted on the `\\src\\app\\studio\\[[...tool]]\\page.tsx` route
 */

import {{ visionTool }} from "@sanity/vision";
import {{ defineConfig }} from "sanity";
import {{ structureTool }} from "sanity/structure";
import {{ internationalizedArray }} from 'sanity-plugin-internationalized-array';

// Go to https://www.sanity.io/docs/api-versioning to learn how API versioning works
import {{ apiVersion, dataset, projectId }} from "./src/sanity/env";
import {{ schemaTypes }} from "../schemaTypes/index";
import {{ structure }} from "./src/sanity/structure";

const SUPPORTED_LOCALES = [
  {languages_config},
];

export default defineConfig({{
  basePath: "/studio",
  projectId,
  dataset,
  // Add and edit the content schema in the '../schemaTypes' folder
  schema: {{
    types: schemaTypes,
  }},
  plugins: [
    structureTool({{ structure }}),
    // Vision is for querying with GROQ from inside the Studio
    // https://www.sanity.io/docs/the-vision-plugin
    visionTool({{ defaultApiVersion: apiVersion }}),
    // Internationalization plugin
    internationalizedArray({{
      languages: SUPPORTED_LOCALES,
      defaultLanguages: [{default_languages_config}],
      fieldTypes: [{field_types_config}],
    }}),
  ],
}});
"""

    def _generate_basic_config_template(self) -> str:
        """Generate basic config template without i18n"""
        return """'use client'

/**
 * This configuration is used to for the Sanity Studio that's mounted on the `\\src\\app\\studio\\[[...tool]]\\page.tsx` route
 */

import { visionTool } from "@sanity/vision";
import { defineConfig } from "sanity";
import { structureTool } from "sanity/structure";

// Go to https://www.sanity.io/docs/api-versioning to learn how API versioning works
import { apiVersion, dataset, projectId } from "./src/sanity/env";
import { schemaTypes } from "../schemaTypes/index";
import { structure } from "./src/sanity/structure";

export default defineConfig({
  basePath: "/studio",
  projectId,
  dataset,
  // Add and edit the content schema in the '../schemaTypes' folder
  schema: {
    types: schemaTypes,
  },
  plugins: [
    structureTool({ structure }),
    // Vision is for querying with GROQ from inside the Studio
    // https://www.sanity.io/docs/the-vision-plugin
    visionTool({ defaultApiVersion: apiVersion }),
  ],
});
"""


class FileGenerator:
    """Enhanced file generation system"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.text_processor = TextProcessor()
        self.template_generator = TemplateGenerator(config)

    def generate_global_structure(self, plan: dict) -> bool:
        """Generate/update structure.ts file"""
        global_docs = [
            doc
            for doc in plan.get("documents", [])
            if doc in ["siteSettings", "header", "footer"]
        ]

        if not global_docs:
            logging.info("No global documents found, skipping structure.ts generation")
            return True

        try:
            structure_content = self.template_generator.generate_structure_template(
                plan
            )

            # Ensure directory exists
            structure_file = Path(self.config.project.structure_file)
            structure_file.parent.mkdir(parents=True, exist_ok=True)

            # Write the structure file
            structure_file.write_text(structure_content, encoding="utf-8")

            logging.info(
                f"✅ Generated structure.ts with global documents configuration:"
            )
            logging.info(f"   - Global documents: {', '.join(global_docs)}")

            return True

        except Exception as e:
            logging.error(f"❌ Could not generate structure.ts: {e}")
            return False

    def update_sanity_config_with_i18n(self) -> bool:
        """Update sanity.config.ts with configuration"""
        config_file = Path(self.config.project.config_file)

        if not config_file.exists():
            logging.warning(
                f"⚠️  {self.config.project.config_file} not found in current directory"
            )
            return False

        try:
            config_content = config_file.read_text(encoding="utf-8")

            logging.info("🔧 Updating sanity.config.ts with configuration...")

            # Check if already configured
            has_i18n = (
                "internationalizedArray" in config_content
                and "SUPPORTED_LOCALES" in config_content
            )
            has_structure = "structure" in config_content

            if has_i18n and has_structure:
                logging.info("✅ sanity.config.ts already properly configured")
                return True

            # Generate new configuration
            new_config_content = (
                self.template_generator.generate_sanity_config_template()
            )

            # Write the updated configuration
            config_file.write_text(new_config_content, encoding="utf-8")

            if self.config.i18n.enabled:
                logging.info("✅ Updated sanity.config.ts with:")
                logging.info("   - Internationalization plugin configuration")
                logging.info(
                    f"   - Supported languages: {', '.join([lang.title for lang in self.config.i18n.supported_languages])}"
                )
                logging.info(f"   - Correct schema import path")
                logging.info(
                    f"   - Field types: {', '.join(self.config.i18n.field_types)}"
                )
            else:
                logging.info("✅ Updated sanity.config.ts with basic configuration")

            return True

        except Exception as e:
            logging.error(f"❌ Could not update sanity.config.ts: {e}")
            return False

    def generate_all_files(self, all_schemas: List[dict], plan: dict):
        """Generate all schema files and index"""
        logging.info("\n--- 💾 PHASE 4: Generating All Project Files ---")

        schemas_dir = Path(self.config.project.schemas_dir)

        # Clean and create directories
        if schemas_dir.exists():
            shutil.rmtree(schemas_dir)

        for folder in ["documents", "objects"]:
            (schemas_dir / folder).mkdir(parents=True, exist_ok=True)

        # Write individual schema files
        all_schema_names = []
        for schema_data in all_schemas:
            schema_name = schema_data["name"]
            folder = "documents" if schema_data["type"] == "document" else "objects"
            file_name = f"{self.text_processor.to_kebab_case(schema_name)}.ts"
            file_path = schemas_dir / folder / file_name

            file_path.write_text(schema_data["code"], encoding="utf-8")
            logging.info(
                f"   ✅ Wrote {folder.upper()[:-1]} SCHEMA: {folder}/{file_name}"
            )
            all_schema_names.append(schema_name)

        # Generate main index file
        self._generate_index_file(schemas_dir, all_schemas, all_schema_names)

    def _generate_index_file(
        self, schemas_dir: Path, all_schemas: List[dict], all_schema_names: List[str]
    ):
        """Generate the main index.ts file"""
        imports = []
        for name in sorted(all_schema_names):
            schema_info = next((s for s in all_schemas if s["name"] == name), None)
            folder = "documents" if schema_info["type"] == "document" else "objects"
            imports.append(
                f"import {name} from './{folder}/{self.text_processor.to_kebab_case(name)}'"
            )

        index_content = (
            f"// This file is auto-generated by the AI Schema Architect.\n"
            f"{chr(10).join(imports)}\n\n"
            f"export const schemaTypes = [\n  {',\n  '.join(sorted(all_schema_names))},\n];\n"
        )

        index_file = schemas_dir / "index.ts"
        index_file.write_text(index_content, encoding="utf-8")
        logging.info(f"   ✅ Wrote main schema index file: {schemas_dir}/index.ts")


# --- 🚀 7. ENHANCED MAIN EXECUTION FLOW ---


class SchemaArchitect:
    """Main application orchestrator"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = Logger(config.project)
        self.figma_client = FigmaClient(config.figma)
        self.ai_architect = AIArchitect(config)
        self.code_corrector = CodeCorrector(config)
        self.code_validator = CodeValidator(config)
        self.file_generator = FileGenerator(config)
        self.text_processor = TextProcessor()

    def run(self):
        """Main execution flow"""
        logging.info("🚀 AI Schema Architect (Enhanced) Initializing... 🚀")

        try:
            # Get Figma sections
            sections = self.figma_client.get_page_sections()
            if not sections:
                logging.critical(
                    "❌ No Figma sections found. Check page/frame names. Exiting."
                )
                return

            # Phase 1: Create architectural plan
            plan = self.ai_architect.phase_one_architect_plan(sections)
            if not plan:
                logging.critical(
                    "❌ Failed to generate architectural plan. Check logs for details. Exiting."
                )
                return

            # Get all valid schema names
            all_valid_names = set(plan.get("documents", [])) | set(
                plan.get("objects", [])
            )
            logging.info(
                f"📋 Plan created. Valid schema names: {sorted(list(all_valid_names))}"
            )

            # Phase 2: Generate schemas
            all_schema_data = self._generate_all_schemas(
                plan, sections, all_valid_names
            )
            if not all_schema_data:
                logging.critical("❌ No schemas were generated in Phase 2. Exiting.")
                return

            # Phase 3: Correct and validate
            corrected_schemas = self._correct_and_validate_schemas(
                all_schema_data, all_valid_names
            )

            # Phase 4: Generate files
            self.file_generator.generate_all_files(corrected_schemas, plan)

            # Generate additional files
            structure_generated = self.file_generator.generate_global_structure(plan)
            config_updated = self.file_generator.update_sanity_config_with_i18n()

            # Show completion message
            self._show_completion_message(structure_generated, config_updated)

        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}", exc_info=True)
            sys.exit(1)

    def _generate_all_schemas(
        self, plan: dict, sections: List[dict], all_valid_names: Set[str]
    ) -> List[dict]:
        """Generate all schema code"""
        all_schema_data = []
        all_planned_schemas = [
            {"name": name, "type": "document"} for name in plan.get("documents", [])
        ] + [{"name": name, "type": "object"} for name in plan.get("objects", [])]

        for schema_info in all_planned_schemas:
            ts_code = self.ai_architect.phase_two_generate_schema_code(
                schema_info["name"], schema_info["type"], plan, sections
            )
            if ts_code:
                all_schema_data.append(
                    {
                        "name": schema_info["name"],
                        "type": schema_info["type"],
                        "code": ts_code,
                    }
                )

        return all_schema_data

    def _correct_and_validate_schemas(
        self, all_schema_data: List[dict], all_valid_names: Set[str]
    ) -> List[dict]:
        """Correct and validate all schemas"""
        logging.info("\n🔍 PHASE 3: Correcting and validating all generated code...")

        corrected_schemas = []
        for schema in all_schema_data:
            logging.info(f"  -> Correcting {schema['name']}...")

            # Apply corrections
            corrected_code = self.code_corrector.correct_generated_code(
                schema["code"], all_valid_names, schema["type"]
            )

            # Validate the corrected code
            issues = self.code_validator.validate_generated_code(
                corrected_code, schema["name"]
            )

            corrected_schemas.append({**schema, "code": corrected_code})

        logging.info("✅ PHASE 3: Code correction complete.")
        return corrected_schemas

    def _show_completion_message(self, structure_generated: bool, config_updated: bool):
        """Show completion message with next steps"""
        logging.info("\n✨ All Done! High-Quality, SEO-Enabled Schemas Generated! ✨")

        print("\n--- NEXT STEPS ---")
        print(
            f"1. ✅ Generated schemas in '{self.config.project.schemas_dir}' with auto-corrected code."
        )

        if structure_generated:
            print("2. ✅ Generated structure.ts with global document configuration!")
            print("   - Header, Footer, and Site Settings are now global documents")
            print("   - Organized for easy content management")
        else:
            print("2. ⚠️  structure.ts was not generated - please check manually.")

        if config_updated:
            if self.config.i18n.enabled:
                print(
                    "3. ✅ Automatically configured sanity.config.ts with internationalization!"
                )
                languages = ", ".join(
                    [lang.title for lang in self.config.i18n.supported_languages]
                )
                print(
                    f"4. ✅ Added {languages} language support with proper field types."
                )
                print("5. **INSTALL REQUIRED PLUGIN:**")
                print("   Run: `npm install sanity-plugin-internationalized-array`")
            else:
                print("3. ✅ Automatically configured sanity.config.ts!")
                print("5. **NO ADDITIONAL PLUGINS REQUIRED**")
        else:
            print("3. ⚠️  sanity.config.ts was not updated - please check manually.")

        print("\n6. **START YOUR DEVELOPMENT SERVER:**")
        print("   Run: `npm run dev`")
        print("   Open: http://localhost:3000/studio")

        if self.config.i18n.enabled:
            print("\n7. **ENJOY YOUR SEO + INTERNATIONALIZED SCHEMA:**")
            languages = "/".join(
                [lang.title for lang in self.config.i18n.supported_languages]
            )
            print(
                f"   🌍 You should now see language tabs ({languages}) on all content fields!"
            )
        else:
            print("\n7. **ENJOY YOUR SEO-ENABLED SCHEMA:**")

        print("   🔧 Header, Footer, and Site Settings are global documents!")
        print("   📈 SEO fields automatically included in page documents!")
        print("   📝 Create new pages and content with structured data!")
        print("   🎨 All schemas are generated from your Figma design!")


def main():
    """Main entry point"""
    try:
        config = AppConfig.from_env()
        architect = SchemaArchitect(config)
        architect.run()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
