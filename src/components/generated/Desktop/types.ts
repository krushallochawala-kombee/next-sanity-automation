// Define types that match the internationalized array structure
export interface InternationalizedStringValue {
  _key: string;
  value?: string;
}

export interface InternationalizedTextValue {
  _key: string;
  value?: string;
}

export interface InternationalizedImageValue {
  _key: string;
  value?: {
    asset?: {
      url: string;
      altText?: string;
    };
  };
}

export interface InternationalizedSlugValue {
  _key: string;
  value?: {
    current?: string;
  };
}

export interface Link {
  _key: string;
  _type: 'link';
  label?: InternationalizedStringValue[];
  externalUrl?: InternationalizedStringValue[];
  internalLink?: {
    slug?: InternationalizedSlugValue[];
  };
}

export interface Button {
  _key: string;
  _type: 'button';
  label?: InternationalizedStringValue[];
  link?: Link;
}

export interface CompanyLogo {
  _id: string;
  _type: 'companylogo';
  name?: InternationalizedStringValue[];
  logo?: InternationalizedImageValue[];
  altText?: InternationalizedStringValue[];
  url?: InternationalizedStringValue[];
}

export interface Feature {
  _id: string;
  _type: 'feature';
  title?: InternationalizedStringValue[];
  description?: InternationalizedTextValue[];
  icon?: InternationalizedImageValue[];
}

export interface MetricItem {
  _key: string;
  _type: 'metricitem';
  value?: InternationalizedStringValue[];
  label?: InternationalizedTextValue[];
  icon?: InternationalizedImageValue[];
}

export interface FooterLinksColumn {
  _key: string;
  _type: 'footerlinkscolumn';
  title?: InternationalizedStringValue[];
  links?: Link[];
}

// Section Types
export interface HeroSection {
  _key: string;
  _type: 'herosection';
  headline?: InternationalizedStringValue[];
  tagline?: InternationalizedTextValue[];
  image?: InternationalizedImageValue[];
  ctaButtons?: Button[];
}

export interface SocialProofSection {
  _key: string;
  _type: 'socialproofsection';
  title?: InternationalizedStringValue[];
  description?: InternationalizedTextValue[];
  logos?: CompanyLogo[];
}

export interface FeaturesSection {
  _key: string;
  _type: 'featuressection';
  title?: InternationalizedStringValue[];
  description?: InternationalizedTextValue[];
  features?: Feature[];
}

export interface QuoteSection {
  _key: string;
  _type: 'quotesection';
  quote?: InternationalizedTextValue[];
  authorName?: InternationalizedStringValue[];
  authorTitle?: InternationalizedStringValue[];
  authorImage?: InternationalizedImageValue[];
}

export interface MetricsSection {
  _key: string;
  _type: 'metricssection';
  title?: InternationalizedStringValue[];
  description?: InternationalizedTextValue[];
  metrics?: MetricItem[];
}

export interface CtaSection {
  _key: string;
  _type: 'ctasection';
  title?: InternationalizedStringValue[];
  description?: InternationalizedTextValue[];
  image?: InternationalizedImageValue[];
  button?: Button;
}

export interface ImageWithAlt {
  _key: string;
  _type: 'imagewithalt';
  image?: InternationalizedImageValue[];
  altText?: InternationalizedStringValue[];
  caption?: InternationalizedTextValue[];
}

export type PageBuilderBlock =
  | HeroSection
  | SocialProofSection
  | FeaturesSection
  | QuoteSection
  | MetricsSection
  | CtaSection
  | ImageWithAlt;

export interface PageData {
  _id: string;
  _type: 'page';
  title?: InternationalizedStringValue[];
  slug?: InternationalizedSlugValue[];
  pageBuilder?: PageBuilderBlock[];
}

// Global Components Data (inferred from design and common patterns, extending minimal schemas)
export interface HeaderData {
  _id: string;
  _type: 'header';
  logo?: CompanyLogo; // Assuming Header can reference a CompanyLogo for its logo
  mainNavigation?: Link[]; // Assuming Header has an array of Links for navigation
  ctaButton?: Button; // Assuming Header has a single CTA button
}

export interface FooterData {
  _id: string;
  _type: 'footer';
  linkColumns?: FooterLinksColumn[];
  logo?: CompanyLogo; // Assuming Footer can reference a CompanyLogo for its logo
  copyrightText?: InternationalizedStringValue[]; // Assuming Footer has a copyright text field
}

export interface SiteSettingsData {
  siteName?: InternationalizedStringValue[];
  siteDescription?: InternationalizedTextValue[];
}

export interface DesktopData {
  page: PageData | null;
  header: HeaderData | null;
  footer: FooterData | null;
  siteSettings: SiteSettingsData | null;
}