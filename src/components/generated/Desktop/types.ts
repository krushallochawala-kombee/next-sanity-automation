import type {
  SanityImageCrop,
  SanityImageHotspot,
} from "@sanity/image-url/lib/types/types";
import { PortableTextBlock } from "@portabletext/types";

// Helper type for Portable Text fields
export type PortableTextContent = PortableTextBlock[];

// Represents the projected image asset data from Sanity
export interface SanityAssetData {
  url: string;
  altText?: string; // From SanityImageAsset.altText
  caption?: string; // From SanityImageAsset.description (often used for caption)
}

// Schema: Imagewithalt
export interface ImageWithAlt {
  _type: "imagewithalt";
  asset?: SanityAssetData; // The actual image asset data (from Imagewithalt.image.asset)
  altText?: PortableTextContent; // Optional override/supplemental alt text (Portable Text from Imagewithalt)
  caption?: PortableTextContent; // Optional override/supplemental caption (Portable Text from Imagewithalt)
}

// Schema: Companylogo
export interface CompanyLogo {
  _type: "companylogo";
  name?: PortableTextContent;
  logo?: SanityAssetData; // The actual logo asset data (from Companylogo.logo.asset)
  altText?: PortableTextContent; // Optional override/supplemental alt text (Portable Text from Companylogo)
  url?: PortableTextContent; // Portable Text, but will be treated as string for URL
}

// Schema: Link
export interface Link {
  _type: "link";
  label?: PortableTextContent;
  externalUrl?: PortableTextContent; // Portable Text, but will be treated as string for URL
  internalLink?: {
    _ref: string;
    _type: "reference";
    slug?: { current: string }; // Expanded slug for internal links
  };
}

// Schema: Button
export interface Button {
  _type: "button";
  label?: PortableTextContent;
  link?: Link; // Reference to Link
}

// Schema: Feature
export interface Feature {
  _type: "feature";
  title?: PortableTextContent;
  description?: PortableTextContent;
  icon?: ImageWithAlt; // Reference to ImageWithAlt for the icon
}

// Schema: Metricitem
export interface MetricItem {
  _type: "metricitem";
  value?: PortableTextContent;
  label?: PortableTextContent;
  icon?: ImageWithAlt; // Reference to ImageWithAlt for the icon
}

// Schema: Herosection
export interface HeroSection {
  _type: "herosection";
  headline?: PortableTextContent;
  tagline?: PortableTextContent;
  image?: ImageWithAlt; // Reference to ImageWithAlt for the main image
  ctaButtons?: Button[]; // Array of Button references (assuming plural for design)
  // Custom fields based on design (not explicitly in provided schema)
  pretitle?: PortableTextContent;
  pretitleLink?: Link;
}

// Schema: Socialproofsection
export interface SocialProofSection {
  _type: "socialproofsection";
  title?: PortableTextContent;
  logos?: CompanyLogo[]; // Array of CompanyLogo references
}

// Schema: Featuressection
export interface FeaturesSection {
  _type: "featuressection";
  name?: string; // String
  title?: PortableTextContent;
  description?: PortableTextContent;
  features?: Feature[]; // Array of Feature references
}

// Schema: Quotesection
export interface QuoteSection {
  _type: "quotesection";
  quote?: PortableTextContent;
  authorName?: PortableTextContent;
  authorTitle?: PortableTextContent;
  authorImage?: ImageWithAlt; // Reference to ImageWithAlt for the author's image
}

// Schema: Metricssection
export interface MetricsSection {
  _type: "metricssection";
  title?: PortableTextContent;
  description?: PortableTextContent;
  metrics?: MetricItem[]; // Array of MetricItem references
  // Custom fields based on design (not explicitly in provided schema)
  pretitle?: PortableTextContent;
  image?: ImageWithAlt; // Reference to ImageWithAlt for the section image
}

// Schema: Ctasection
export interface CtaSection {
  _type: "ctasection";
  title?: PortableTextContent;
  description?: PortableTextContent;
  image?: ImageWithAlt; // Reference to ImageWithAlt for the section image
  ctaButtons?: Button[]; // Array of Button references (assuming plural for design)
}

// Schema: Footerlink
export interface FooterLink {
  _type: "footerlink";
  label?: PortableTextContent;
  link?: Link; // Reference to Link
}

// Schema: Footerlinkscolumn
export interface FooterLinksColumn {
  _type: "footerlinkscolumn";
  title?: PortableTextContent;
  links?: FooterLink[]; // Array of FooterLink references
}

// Schema: Footer
export interface Footer {
  _type: "footer";
  linkColumns?: FooterLinksColumn[]; // Array of FooterLinksColumn references
  logo?: CompanyLogo; // Reference to CompanyLogo
}

// Schema: Header
export interface Header {
  _type: "header";
  logo?: CompanyLogo; // Reference to CompanyLogo
}

// Schema: SiteSettings
export interface SiteSettings {
  _type: "siteSettings";
  siteName?: PortableTextContent;
  siteDescription?: PortableTextContent;
  header?: Header; // Reference to Header
  footer?: Footer; // Reference to Footer
}

// Schema: Page
export interface Page {
  _type: "page";
  title?: PortableTextContent;
  slug?: { current: string };
  pageBuilder?: (
    | HeroSection
    | SocialProofSection
    | FeaturesSection
    | QuoteSection
    | MetricsSection
    | CtaSection
  )[];
}

// Main type for the Desktop component, combining Page and SiteSettings
export interface DesktopData {
  page: Page;
  siteSettings: SiteSettings;
}
