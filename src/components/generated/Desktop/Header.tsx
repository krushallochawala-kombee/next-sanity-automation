'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
// import { urlForImage } from '@/sanity/lib/image'; // Assuming you have a urlForImage helper
import type {
  HeaderData,
  InternationalizedStringValue,
  InternationalizedTextValue,
  InternationalizedImageValue,
  InternationalizedSlugValue,
  Link as LinkType,
  Button as ButtonType,
} from './types';

// Helper function to extract string from internationalized array
const getInternationalizedString = (data: unknown): string => {
  if (!data) return '';
  if (Array.isArray(data) && data.length > 0) {
    const firstItem = data[0];
    if (firstItem && typeof firstItem === 'object' && firstItem !== null && 'value' in firstItem) {
      const typedItem = firstItem as InternationalizedStringValue | InternationalizedTextValue;
      return typedItem.value || '';
    }
  }
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
      //     url: urlForImage(typedItem.value.asset.url).url(),
      //     altText: typedItem.value.asset.altText || '',
      //   };
      // }
    }
  }
  return null;
};

interface HeaderProps {
  data: HeaderData | null;
  siteName?: string;
}

export default function Header({ data, siteName }: HeaderProps) {
  // 🚨 CRITICAL: If no data from Sanity, render NOTHING
  if (!data && !siteName) return null;

  const logoImage = getInternationalizedImage(data?.logo?.logo);
  const logoAltText = getInternationalizedString(data?.logo?.altText);
  const logoName = getInternationalizedString(data?.logo?.name);
  const mainNavigation = data?.mainNavigation?.filter(item => item !== null);
  const ctaButton = data?.ctaButton;

  const renderLink = (linkData: LinkType, key: string) => {
    const label = getInternationalizedString(linkData.label);
    const externalUrl = getInternationalizedString(linkData.externalUrl);
    const internalSlug = getInternationalizedString(linkData.internalLink?.slug);
    const href = externalUrl || (internalSlug ? `/${internalSlug}` : '#');

    if (!label) return null;

    return (
      <Link key={key} href={href} className="text-gray-600 hover:text-gray-900 px-3 py-2">
        {label}
      </Link>
    );
  };

  const renderButton = (buttonData: ButtonType | undefined, key: string) => {
    if (!buttonData || !getInternationalizedString(buttonData.label)) return null;

    const label = getInternationalizedString(buttonData.label);
    const externalUrl = getInternationalizedString(buttonData.link?.externalUrl);
    const internalSlug = getInternationalizedString(buttonData.link?.internalLink?.slug);
    const href = externalUrl || (internalSlug ? `/${internalSlug}` : '#');

    return (
      <Link key={key} href={href} className="ml-4 px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition-colors">
        {label}
      </Link>
    );
  };

  return (
    <header className="bg-white shadow-sm py-4">
      <div className="container mx-auto px-4 flex justify-between items-center">
        {/* Logo */}
        <div className="flex items-center">
          {(logoImage || logoName || siteName) ? (
            <Link href="/" className="flex items-center space-x-2">
              {logoImage && (
                <Image
                  src={logoImage.url}
                  alt={logoAltText || logoName || siteName || 'Site logo'}
                  width={32}
                  height={32}
                  className="h-8 w-8 object-contain"
                />
              )}
              {(logoName || siteName) && (
                <span className="text-xl font-bold text-gray-900">{logoName || siteName}</span>
              )}
            </Link>
          ) : null}
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-1">
          {mainNavigation && mainNavigation.length > 0 && (
            mainNavigation.map((item, index) => renderLink(item, item._key || `nav-link-${index}`))
          )}
        </nav>

        {/* CTA Button */}
        <div className="flex items-center">
          {renderButton(ctaButton, ctaButton?._key || 'header-cta')}
        </div>
      </div>
    </header>
  );
}