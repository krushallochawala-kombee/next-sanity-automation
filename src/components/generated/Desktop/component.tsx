'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
// import { urlForImage } from '@/sanity/lib/image'; // Assuming you have a urlForImage helper
import Header from './Header';
import Footer from './Footer';
import type {
  DesktopData,
  InternationalizedStringValue,
  InternationalizedTextValue,
  InternationalizedImageValue,
  InternationalizedSlugValue,
  Link as LinkType,
  Button as ButtonType,
  CompanyLogo,
  Feature,
  MetricItem,
  FooterLinksColumn,
  HeroSection,
  SocialProofSection,
  FeaturesSection,
  QuoteSection,
  MetricsSection,
  CtaSection,
  ImageWithAlt,
} from './types';

// Helper function to extract string from internationalized array
const getInternationalizedString = (data: unknown): string => {
  if (!data) return '';

  // Handle internationalized array
  if (Array.isArray(data) && data.length > 0) {
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {
      const typedItem = firstItem as InternationalizedStringValue | InternationalizedTextValue;
      return typedItem.value || '';
    }
  }

  // Handle simple string (though schemas indicate arrays for internationalized strings)
  if (typeof data === 'string') {
    return data;
  }

  return '';
};

// Helper function to extract image from internationalized array
const getInternationalizedImage = (
  data: unknown
): { url: string; altText?: string } | null => {
  if (!data) return null;

  if (Array.isArray(data) && data.length > 0) {
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {
      const typedItem = firstItem as InternationalizedImageValue;
      // if (typedItem.value?.asset?.url) {
      //   return {
      //     url: urlForImage(typedItem.value.asset.url).url(), // Use Sanity's image URL builder
      //     altText: typedItem.value.asset.altText || '',
      //   };
      // }
    }
  }

  return null;
};

// Helper to render a button
const renderButton = (buttonData: ButtonType | undefined, key: string) => {
  if (!buttonData || !getInternationalizedString(buttonData.label)) return null;

  const label = getInternationalizedString(buttonData.label);
  const externalUrl = getInternationalizedString(buttonData.link?.externalUrl);
  const internalSlug = getInternationalizedString(buttonData.link?.internalLink?.slug);
  const href = externalUrl || (internalSlug ? `/${internalSlug}` : '#');

  return (
    <Link key={key} href={href} className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors">
      {label}
    </Link>
  );
};

interface DesktopProps {
  data: DesktopData;
}

export default function Desktop({ data }: DesktopProps) {
  if (!data || !data.page) {
    return null; // Or a loading/error state
  }

  const { page, header, footer, siteSettings } = data;

  return (
    <div className="min-h-screen flex flex-col">
      <Header data={header} siteName={getInternationalizedString(siteSettings?.siteName)} />

      <main className="flex-grow">
        {page.pageBuilder?.filter(block => block !== null).map((block) => {
          switch (block._type) {
            case 'herosection': {
              const section = block as HeroSection;
              const headline = getInternationalizedString(section.headline);
              const tagline = getInternationalizedString(section.tagline);
              const image = getInternationalizedImage(section.image);
              const ctaButtons = section.ctaButtons?.filter(btn => btn !== null);

              return (
                <section key={block._key} className="py-16 text-center bg-gray-50">
                  <div className="container mx-auto px-4">
                    {headline && <h1 className="text-5xl font-bold mb-4">{headline}</h1>}
                    {tagline && <p className="text-xl text-gray-600 mb-8">{tagline}</p>}
                    <div className="flex justify-center space-x-4 mb-12">
                      {ctaButtons?.map((button, index) => renderButton(button, button._key || `hero-btn-${index}`))}
                    </div>
                    {image && (
                      <div className="relative w-full max-w-4xl mx-auto h-96">
                        <Image
                          src={image.url}
                          alt={image.altText || headline || 'Hero image'}
                          fill
                          style={{ objectFit: 'contain' }}
                          className="rounded-lg shadow-xl"
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1000px"
                        />
                      </div>
                    )}
                  </div>
                </section>
              );
            }
            case 'socialproofsection': {
              const section = block as SocialProofSection;
              const title = getInternationalizedString(section.title);
              const description = getInternationalizedString(section.description);
              const logos = section.logos?.filter(logo => logo !== null);

              return (
                <section key={block._key} className="py-12 bg-white">
                  <div className="container mx-auto px-4 text-center">
                    {title && <h2 className="text-3xl font-bold mb-2">{title}</h2>}
                    {description && <p className="text-lg text-gray-600 mb-8">{description}</p>}
                    {logos && logos.length > 0 && (
                      <div className="flex flex-wrap justify-center items-center gap-8">
                        {logos.map((logoItem, index) => {
                          const logoImage = getInternationalizedImage(logoItem.logo);
                          const logoName = getInternationalizedString(logoItem.name);
                          const logoAltText = getInternationalizedString(logoItem.altText);
                          const logoUrl = getInternationalizedString(logoItem.url);

                          return (
                            <div key={logoItem._id || `logo-${index}`} className="flex-shrink-0">
                              {logoImage ? (
                                <Link href={logoUrl || '#'} target="_blank" rel="noopener noreferrer">
                                  <Image
                                    src={logoImage.url}
                                    alt={logoAltText || logoName || 'Company logo'}
                                    width={120}
                                    height={40}
                                    className="h-10 object-contain"
                                  />
                                </Link>
                              ) : logoName ? (
                                <Link href={logoUrl || '#'} target="_blank" rel="noopener noreferrer" className="text-lg font-semibold text-gray-800">
                                  {logoName}
                                </Link>
                              ) : null}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </section>
              );
            }
            case 'featuressection': {
              const section = block as FeaturesSection;
              const title = getInternationalizedString(section.title);
              const description = getInternationalizedString(section.description);
              const features = section.features?.filter(feature => feature !== null);

              return (
                <section key={block._key} className="py-16 bg-gray-50">
                  <div className="container mx-auto px-4 text-center">
                    {title && <h2 className="text-4xl font-bold mb-4">{title}</h2>}
                    {description && <p className="text-xl text-gray-600 mb-12">{description}</p>}
                    {features && features.length > 0 && (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {features.map((featureItem, index) => {
                          const featureTitle = getInternationalizedString(featureItem.title);
                          const featureDescription = getInternationalizedString(featureItem.description);
                          const featureIcon = getInternationalizedImage(featureItem.icon);

                          return (
                            <div key={featureItem._id || `feature-${index}`} className="p-6 bg-white rounded-lg shadow-md text-left">
                              {featureIcon && (
                                <div className="mb-4">
                                  <Image
                                    src={featureIcon.url}
                                    alt={featureIcon.altText || featureTitle || 'Feature icon'}
                                    width={48}
                                    height={48}
                                    className="h-12 w-12 object-contain"
                                  />
                                </div>
                              )}
                              {featureTitle && <h3 className="text-xl font-semibold mb-2">{featureTitle}</h3>}
                              {featureDescription && <p className="text-gray-600">{featureDescription}</p>}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </section>
              );
            }
            case 'quotesection': {
              const section = block as QuoteSection;
              const quote = getInternationalizedString(section.quote);
              const authorName = getInternationalizedString(section.authorName);
              const authorTitle = getInternationalizedString(section.authorTitle);
              const authorImage = getInternationalizedImage(section.authorImage);

              return (
                <section key={block._key} className="py-16 bg-white">
                  <div className="container mx-auto px-4 text-center max-w-3xl">
                    {quote && <p className="text-3xl font-medium text-gray-800 mb-8">&ldquo;{quote}&rdquo;</p>}
                    {(authorImage || authorName || authorTitle) && (
                      <div className="flex flex-col items-center">
                        {authorImage && (
                          <div className="mb-4">
                            <Image
                              src={authorImage.url}
                              alt={authorImage.altText || authorName || 'Author image'}
                              width={64}
                              height={64}
                              className="rounded-full object-cover"
                            />
                          </div>
                        )}
                        {authorName && <p className="text-lg font-semibold text-gray-900">{authorName}</p>}
                        {authorTitle && <p className="text-md text-gray-600">{authorTitle}</p>}
                      </div>
                    )}
                  </div>
                </section>
              );
            }
            case 'metricssection': {
              const section = block as MetricsSection;
              const title = getInternationalizedString(section.title);
              const description = getInternationalizedString(section.description);
              const metrics = section.metrics?.filter(metric => metric !== null);

              return (
                <section key={block._key} className="py-16 bg-gray-50">
                  <div className="container mx-auto px-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                      <div className="text-left">
                        {title && <h2 className="text-4xl font-bold mb-4">{title}</h2>}
                        {description && <p className="text-xl text-gray-600 mb-8">{description}</p>}
                        {metrics && metrics.length > 0 && (
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                            {metrics.map((metricItem, index) => {
                              const metricValue = getInternationalizedString(metricItem.value);
                              const metricLabel = getInternationalizedString(metricItem.label);
                              const metricIcon = getInternationalizedImage(metricItem.icon);

                              return (
                                <div key={metricItem._key || `metric-${index}`} className="flex items-start space-x-4">
                                  {metricIcon && (
                                    <Image
                                      src={metricIcon.url}
                                      alt={metricIcon.altText || metricLabel || 'Metric icon'}
                                      width={32}
                                      height={32}
                                      className="h-8 w-8 object-contain"
                                    />
                                  )}
                                  <div>
                                    {metricValue && <p className="text-4xl font-bold text-gray-900">{metricValue}</p>}
                                    {metricLabel && <p className="text-lg text-gray-600">{metricLabel}</p>}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                      {/* The image for this section is handled by a separate ImageWithAlt block */}
                    </div>
                  </div>
                </section>
              );
            }
            case 'imagewithalt': { // For the whiteboard image in the metrics section
              const section = block as ImageWithAlt;
              const image = getInternationalizedImage(section.image);
              const altText = getInternationalizedString(section.altText);
              const caption = getInternationalizedString(section.caption);

              return (
                <section key={block._key} className="py-8 bg-gray-50">
                  <div className="container mx-auto px-4">
                    {image && (
                      <div className="relative w-full max-w-4xl mx-auto h-96">
                        <Image
                          src={image.url}
                          alt={altText || 'Section image'}
                          fill
                          style={{ objectFit: 'cover' }}
                          className="rounded-lg shadow-xl"
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1000px"
                        />
                        {caption && <p className="mt-2 text-center text-gray-500 text-sm">{caption}</p>}
                      </div>
                    )}
                  </div>
                </section>
              );
            }
            case 'ctasection': {
              const section = block as CtaSection;
              const title = getInternationalizedString(section.title);
              const description = getInternationalizedString(section.description);
              const button = section.button;

              return (
                <section key={block._key} className="py-16 bg-blue-600 text-white text-center">
                  <div className="container mx-auto px-4 max-w-3xl">
                    {title && <h2 className="text-4xl font-bold mb-4">{title}</h2>}
                    {description && <p className="text-xl mb-8">{description}</p>}
                    <div className="flex justify-center space-x-4">
                      {/* Assuming only one button for CTA section based on schema */}
                      {renderButton(button, button?._key || 'cta-btn')}
                    </div>
                  </div>
                </section>
              );
            }
            default:
              return null;
          }
        })}
      </main>

      <Footer data={footer} siteName={getInternationalizedString(siteSettings?.siteName)} />
    </div>
  );
}