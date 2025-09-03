'use client';

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
// import { urlForImage } from '@/sanity/lib/image'; // Assuming you have a urlForImage helper
import type {
  FooterData,
  InternationalizedStringValue,
  InternationalizedTextValue,
  InternationalizedImageValue,
  InternationalizedSlugValue,
  Link as LinkType,
  FooterLinksColumn,
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
      //     // url: urlForImage(typedItem.value.asset.url).url(),
      //     altText: typedItem.value.asset.altText || '',
      //   };
      // }
    }
  }
  return null;
};

interface FooterProps {
  data: FooterData | null;
  siteName?: string;
}

export default function Footer({ data, siteName }: FooterProps) {
  // 🚨 CRITICAL: If no data from Sanity, render NOTHING
  if (!data && !siteName) return null;

  const logoImage = getInternationalizedImage(data?.logo?.logo);
  const logoAltText = getInternationalizedString(data?.logo?.altText);
  const logoName = getInternationalizedString(data?.logo?.name);
  const linkColumns = data?.linkColumns?.filter(column => column !== null);
  const copyrightText = getInternationalizedString(data?.copyrightText);

  const renderLink = (linkData: LinkType, key: string) => {
    const label = getInternationalizedString(linkData.label);
    const externalUrl = getInternationalizedString(linkData.externalUrl);
    const internalSlug = getInternationalizedString(linkData.internalLink?.slug);
    const href = externalUrl || (internalSlug ? `/${internalSlug}` : '#');

    if (!label) return null;

    return (
      <li key={key} className="mb-2">
        <Link href={href} className="text-gray-600 hover:text-gray-900 text-sm">
          {label}
        </Link>
      </li>
    );
  };

  return (
    <footer className="bg-gray-100 py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-8 border-b pb-8 mb-8">
          {/* Logo and Site Name */}
          <div className="md:col-span-2">
            {(logoImage || logoName || siteName) ? (
              <Link href="/" className="flex items-center space-x-2 mb-4">
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
            {/* Placeholder for site description if needed, but not in design for footer */}
          </div>

          {/* Link Columns */}
          {linkColumns && linkColumns.length > 0 && (
            linkColumns.map((column, colIndex) => {
              const columnTitle = getInternationalizedString(column.title);
              const links = column.links?.filter(link => link !== null);

              if (!columnTitle && (!links || links.length === 0)) return null;

              return (
                <div key={column._key || `footer-col-${colIndex}`} className="md:col-span-1">
                  {columnTitle && <h3 className="text-md font-semibold text-gray-900 mb-4">{columnTitle}</h3>}
                  {links && links.length > 0 && (
                    <ul>
                      {links.map((link, linkIndex) => renderLink(link, link._key || `footer-link-${linkIndex}`))}
                    </ul>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Copyright */}
        <div className="text-center text-gray-500 text-sm">
          {copyrightText && <p>{copyrightText}</p>}
          {!copyrightText && siteName && <p>&copy; {new Date().getFullYear()} {siteName}. All rights reserved.</p>}
        </div>
      </div>
    </footer>
  );
}