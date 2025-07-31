"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import type {
  DesktopData,
  HeroSection,
  SocialProofSection,
  FeaturesSection,
  QuoteSection,
  MetricsSection,
  CtaSection,
  Button,
  CompanyLogo,
} from "./types";

// Type definitions removed - using unknown type for flexibility

// Helper function to extract string from internationalized array or PortableText
const getInternationalizedString = (data: unknown): string => {
  if (!data) return "";

  // Handle internationalized array
  if (Array.isArray(data) && data.length > 0) {
    const firstItem = data[0];
    // If it's an internationalized array item
    if (
      firstItem &&
      typeof firstItem === "object" &&
      firstItem !== null &&
      "value" in firstItem
    ) {
      const typedItem = firstItem as { value?: string };
      return typedItem.value || "";
    }
    // If it's PortableText array, convert to plain text
    if (
      firstItem &&
      typeof firstItem === "object" &&
      firstItem !== null &&
      "_type" in firstItem
    ) {
      const typedItem = firstItem as { _type?: string };
      if (typedItem._type === "block") {
        return toPlainText(data);
      }
    }
  }

  // Handle simple string
  if (typeof data === "string") {
    return data;
  }

  return "";
};

// Helper function to extract image from internationalized array
const getInternationalizedImage = (
  data: unknown
): { url?: string; altText?: string } | null => {
  if (!data) return null;

  // Handle internationalized array
  if (Array.isArray(data) && data.length > 0) {
    const firstItem = data[0];
    if (
      firstItem &&
      typeof firstItem === "object" &&
      firstItem !== null &&
      "value" in firstItem
    ) {
      const typedItem = firstItem as {
        value?: { asset?: { _ref?: string; url?: string; altText?: string } };
      };
      const value = typedItem.value;
      if (!value || !value.asset) return null;

      // Handle asset reference
      if (value.asset._ref) {
        return null;
      }

      return {
        url: value.asset.url,
        altText: value.asset.altText,
      };
    }
  }

  // Handle direct image object
  if (data && typeof data === "object" && data !== null && "asset" in data) {
    const typedData = data as { asset?: { url?: string; altText?: string } };
    if (typedData.asset) {
      return {
        url: typedData.asset.url,
        altText: typedData.asset.altText,
      };
    }
  }

  return null;
};

// Helper function to extract plain text from Portable Text array (keeping for fallback)
const toPlainText = (blocks: unknown): string => {
  if (!blocks || !Array.isArray(blocks) || blocks.length === 0) return "";
  return blocks
    .map((block) => {
      if (
        block &&
        typeof block === "object" &&
        block !== null &&
        "_type" in block
      ) {
        const typedBlock = block as { _type?: string; children?: unknown[] };
        if (typedBlock._type === "block" && typedBlock.children) {
          return typedBlock.children
            .map((child) => {
              if (
                child &&
                typeof child === "object" &&
                child !== null &&
                "text" in child
              ) {
                const typedChild = child as { text?: string };
                return typedChild.text || "";
              }
              return "";
            })
            .join("");
        }
      }
      return "";
    })
    .join("\n");
};

// Helper function to convert Link object to href string
const getLinkHref = (link: unknown): string => {
  if (!link || typeof link !== "object" || link === null) return "#";

  const typedLink = link as {
    externalUrl?: unknown;
    internalLink?: { slug?: unknown };
  };

  // Check for external URL first (internationalized array)
  const externalUrl = getInternationalizedString(typedLink.externalUrl);
  if (externalUrl) return externalUrl;

  // Handle internal link (reference)
  if (typedLink.internalLink?.slug) {
    // Handle internationalized slug
    const slug = getInternationalizedString(typedLink.internalLink.slug);
    if (slug) return `/${slug}`;
  }

  return "#";
};

// Removed portableTextComponents as it's not used with internationalized arrays

interface CustomButtonProps {
  button: Button;
  variant: "primary" | "secondary";
  icon?: React.ReactNode;
}

const CustomButton: React.FC<CustomButtonProps> = ({
  button,
  variant,
  icon,
}) => {
  if (!button || !button.label) return null;

  const label = getInternationalizedString(button.label);
  const href = getLinkHref(button.link);

  const baseClasses =
    "inline-flex items-center justify-center px-6 py-3 border text-base font-medium rounded-lg shadow-sm transition-colors duration-200";
  const primaryClasses =
    "bg-indigo-600 text-white border-transparent hover:bg-indigo-700";
  const secondaryClasses =
    "bg-white text-gray-700 border-gray-300 hover:bg-gray-50";

  return (
    <Link
      href={href}
      className={`${baseClasses} ${variant === "primary" ? primaryClasses : secondaryClasses}`}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {label}
    </Link>
  );
};

const HeroSectionComponent: React.FC<{ data: HeroSection }> = ({ data }) => (
  <section className="relative isolate overflow-hidden bg-white px-6 py-24 sm:py-32 lg:px-8">
    <div className="mx-auto max-w-2xl text-center">
      {data.pretitle && data.pretitleLink && (
        <Link
          href={getLinkHref(data.pretitleLink)}
          className="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-sm font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10 mb-4"
        >
          {getInternationalizedString(data.pretitle)}{" "}
          <span aria-hidden="true" className="ml-1">
            &rarr;
          </span>
        </Link>
      )}
      <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
        {getInternationalizedString(data.headline) || "Welcome to Our Platform"}
      </h1>
      <p className="mt-6 text-lg leading-8 text-gray-600">
        {getInternationalizedString(data.tagline) ||
          "Build something amazing today"}
      </p>
      <div className="mt-10 flex items-center justify-center gap-x-6">
        {data.ctaButtons && data.ctaButtons[0] && (
          <CustomButton
            button={data.ctaButtons[0]}
            variant="secondary"
            icon={
              <svg
                className="h-5 w-5 text-gray-700"
                viewBox="0 0 24 24"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12Zm14.024-.983a1.125 1.125 0 0 1 0 1.966l-5.604 3.113a1.125 1.125 0 0 1-1.726-.986V9.866a1.125 1.125 0 0 1 1.726-.986l5.604 3.113Z"
                  clipRule="evenodd"
                />
              </svg>
            }
          />
        )}
        {data.ctaButtons && data.ctaButtons[1] && (
          <CustomButton button={data.ctaButtons[1]} variant="primary" />
        )}
      </div>
    </div>
    {data.image &&
      (() => {
        const image = getInternationalizedImage(data.image);
        return (
          image?.url && (
            <div className="mt-16 flow-root sm:mt-24">
              <div className="-m-2 rounded-xl bg-gray-900/5 p-2 ring-1 ring-inset ring-gray-900/10 lg:-m-4 lg:rounded-2xl lg:p-4">
                <Image
                  src={image.url}
                  alt={
                    getInternationalizedString(data.image) ||
                    image.altText ||
                    "Hero image"
                  }
                  width={2432}
                  height={1442}
                  className="rounded-md shadow-2xl ring-1 ring-gray-900/10"
                />
              </div>
            </div>
          )
        );
      })()}
  </section>
);

const SocialProofSectionComponent: React.FC<{ data: SocialProofSection }> = ({
  data,
}) => (
  <section className="bg-white py-24 sm:py-32">
    <div className="mx-auto max-w-7xl px-6 lg:px-8">
      <h2 className="text-center text-lg font-semibold leading-8 text-gray-900">
        {getInternationalizedString(data.title) ||
          "Trusted by leading companies"}
      </h2>
      <div className="mx-auto mt-10 grid max-w-lg grid-cols-4 items-center gap-x-8 gap-y-10 sm:max-w-xl sm:grid-cols-6 sm:gap-x-10 lg:mx-0 lg:max-w-none lg:grid-cols-5">
        {data.logos?.map(
          (logo, index) =>
            logo.logo?.url && (
              <Image
                key={index}
                className="col-span-2 max-h-12 w-full object-contain lg:col-span-1"
                src={logo.logo.url}
                alt={
                  getInternationalizedString(logo.altText) ||
                  logo.logo.altText ||
                  getInternationalizedString(logo.name) ||
                  "Company logo"
                }
                width={158}
                height={48}
              />
            )
        )}
      </div>
    </div>
  </section>
);

const FeaturesSectionComponent: React.FC<{ data: FeaturesSection }> = ({
  data,
}) => (
  <section className="bg-white py-24 sm:py-32">
    <div className="mx-auto max-w-7xl px-6 lg:px-8">
      <div className="mx-auto max-w-2xl lg:text-center">
        <h2 className="text-base font-semibold leading-7 text-indigo-600">
          Features
        </h2>
        <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          {getInternationalizedString(data.title) || "Everything you need"}
        </p>
        <p className="mt-6 text-lg leading-8 text-gray-600">
          {getInternationalizedString(data.description) ||
            "Powerful features to help you succeed"}
        </p>
      </div>
      <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
        <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3 lg:gap-y-16">
          {data.features?.map((feature, index) => (
            <div key={index} className="relative pl-16">
              <dt className="text-base font-semibold leading-7 text-gray-900">
                <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                  {feature.icon?.asset?.url && (
                    <Image
                      src={feature.icon.asset.url}
                      alt={
                        getInternationalizedString(feature.icon.altText) ||
                        feature.icon.asset.altText ||
                        getInternationalizedString(feature.title) ||
                        "Feature icon"
                      }
                      width={24}
                      height={24}
                      className="h-6 w-6 text-white"
                      aria-hidden="true"
                    />
                  )}
                </div>
                {getInternationalizedString(feature.title) || "Feature"}
              </dt>
              <dd className="mt-2 text-base leading-7 text-gray-600">
                {getInternationalizedString(feature.description) ||
                  "Feature description"}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  </section>
);

const QuoteSectionComponent: React.FC<{ data: QuoteSection }> = ({ data }) => (
  <section className="bg-white py-24 sm:py-32">
    <div className="mx-auto max-w-7xl px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <figure className="mt-10">
          <blockquote className="text-center text-xl font-semibold leading-8 text-gray-900 sm:text-2xl sm:leading-9">
            <p>
              &ldquo;
              {getInternationalizedString(data.quote) ||
                "Amazing product that transformed our business"}
              &rdquo;
            </p>
          </blockquote>
          <figcaption className="mt-10">
            {data.authorImage?.asset?.url && (
              <Image
                className="mx-auto h-10 w-10 rounded-full"
                src={data.authorImage.asset.url}
                alt={
                  getInternationalizedString(data.authorImage.altText) ||
                  data.authorImage.asset.altText ||
                  getInternationalizedString(data.authorName) ||
                  "Author image"
                }
                width={40}
                height={40}
              />
            )}
            <div className="mt-4 flex items-center justify-center space-x-3 text-base">
              <div className="font-semibold text-gray-900">
                {getInternationalizedString(data.authorName) || "Anonymous"}
              </div>
              <svg
                viewBox="0 0 2 2"
                width={3}
                height={3}
                aria-hidden="true"
                className="fill-gray-900"
              >
                <circle cx={1} cy={1} r={1} />
              </svg>
              <div className="text-gray-600">
                {getInternationalizedString(data.authorTitle) || "Customer"}
              </div>
            </div>
          </figcaption>
        </figure>
      </div>
    </div>
  </section>
);

const MetricsSectionComponent: React.FC<{ data: MetricsSection }> = ({
  data,
}) => (
  <section className="bg-white py-24 sm:py-32">
    <div className="mx-auto max-w-7xl px-6 lg:px-8">
      <div className="mx-auto grid max-w-2xl grid-cols-1 items-start gap-x-8 gap-y-16 sm:gap-y-24 lg:mx-0 lg:max-w-none lg:grid-cols-2">
        <div className="lg:pr-4">
          <div className="relative overflow-hidden rounded-3xl bg-gray-900 px-6 pb-9 pt-64 shadow-xl sm:px-12 lg:px-8 lg:pt-80 xl:px-20 xl:pt-100">
            {data.image?.asset?.url && (
              <Image
                className="absolute inset-0 h-full w-full object-cover"
                src={data.image.asset.url}
                alt={
                  getInternationalizedString(data.image.altText) ||
                  data.image.asset.altText ||
                  "Metrics section image"
                }
                width={1000}
                height={1000}
              />
            )}
          </div>
        </div>
        <div>
          <div className="text-base font-semibold leading-7 text-indigo-600">
            {getInternationalizedString(data.pretitle) || "Our Impact"}
          </div>
          <h2 className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            {getInternationalizedString(data.title) || "Results that matter"}
          </h2>
          <p className="mt-6 text-xl leading-8 text-gray-600">
            {getInternationalizedString(data.description) ||
              "See the measurable impact we deliver"}
          </p>
          <dl className="mt-10 grid grid-cols-1 gap-x-8 gap-y-10 sm:grid-cols-2 lg:pt-2">
            {data.metrics?.map((metric, index) => (
              <div key={index} className="flex flex-col items-start">
                <dt className="mt-4 font-semibold text-gray-900">
                  {metric.icon?.asset?.url && (
                    <Image
                      src={metric.icon.asset.url}
                      alt={
                        getInternationalizedString(metric.icon.altText) ||
                        metric.icon.asset.altText ||
                        getInternationalizedString(metric.label) ||
                        "Metric icon"
                      }
                      width={24}
                      height={24}
                      className="h-6 w-6 text-indigo-600"
                      aria-hidden="true"
                    />
                  )}
                  <p className="text-5xl font-bold text-gray-900 mt-2">
                    {getInternationalizedString(metric.value) || "100%"}
                  </p>
                </dt>
                <dd className="mt-2 text-base leading-7 text-gray-600">
                  {getInternationalizedString(metric.label) || "Success rate"}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  </section>
);

const CtaSectionComponent: React.FC<{ data: CtaSection }> = ({ data }) => (
  <section className="bg-white py-24 sm:py-32">
    <div className="mx-auto max-w-7xl px-6 lg:px-8">
      <div className="relative isolate overflow-hidden bg-gray-900 px-6 py-24 text-center shadow-2xl sm:rounded-3xl sm:px-16">
        <h2 className="mx-auto max-w-2xl text-3xl font-bold tracking-tight text-white sm:text-4xl">
          {getInternationalizedString(data.title) || "Ready to get started?"}
        </h2>
        <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-gray-300">
          {getInternationalizedString(data.description) ||
            "Join thousands of satisfied customers today"}
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          {data.ctaButtons && data.ctaButtons[0] && (
            <CustomButton button={data.ctaButtons[0]} variant="secondary" />
          )}
          {data.ctaButtons && data.ctaButtons[1] && (
            <CustomButton button={data.ctaButtons[1]} variant="primary" />
          )}
        </div>
        <svg
          viewBox="0 0 1024 1024"
          className="absolute left-1/2 top-1/2 -z-10 h-[64rem] w-[64rem] -translate-x-1/2 [mask-image:radial-gradient(closest-side,white,transparent)]"
          aria-hidden="true"
        >
          <circle
            cx={512}
            cy={512}
            r={512}
            fill="url(#82759db1-efc5-47bf-b2fd-520cba108650)"
            fillOpacity="0.7"
          />
          <defs>
            <radialGradient id="82759db1-efc5-47bf-b2fd-520cba108650">
              <stop stopColor="#7775D6" />
              <stop offset={1} stopColor="#E935C1" />
            </radialGradient>
          </defs>
        </svg>
      </div>
    </div>
  </section>
);

const HeaderComponent: React.FC<{ data: CompanyLogo | undefined }> = ({
  data,
}) => (
  <header className="bg-white">
    <nav
      className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8"
      aria-label="Global"
    >
      <div className="flex lg:flex-1">
        <Link href="/" className="-m-1.5 p-1.5">
          <span className="sr-only">Untitled UI</span>
          {data?.logo?.url ? (
            <Image
              className="h-8 w-auto"
              src={data.logo.url}
              alt={
                getInternationalizedString(data.altText) ||
                data.logo.altText ||
                getInternationalizedString(data.name) ||
                "Company logo"
              }
              width={32}
              height={32}
            />
          ) : (
            <span className="text-lg font-bold text-gray-900">Untitled UI</span>
          )}
        </Link>
      </div>
      <div className="flex lg:hidden">
        <button
          type="button"
          className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
        >
          <span className="sr-only">Open main menu</span>
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            />
          </svg>
        </button>
      </div>
      <div className="hidden lg:flex lg:gap-x-12">
        <Link
          href="#"
          className="text-sm font-semibold leading-6 text-gray-900"
        >
          Home
        </Link>
        <Link
          href="#"
          className="text-sm font-semibold leading-6 text-gray-900"
        >
          Products
        </Link>
        <Link
          href="#"
          className="text-sm font-semibold leading-6 text-gray-900"
        >
          Resources
        </Link>
        <Link
          href="#"
          className="text-sm font-semibold leading-6 text-gray-900"
        >
          Pricing
        </Link>
      </div>
      <div className="hidden lg:flex lg:flex-1 lg:justify-end">
        <Link
          href="#"
          className="text-sm font-semibold leading-6 text-gray-900"
        >
          <Image
            src="https://via.placeholder.com/32"
            alt="User Avatar"
            width={32}
            height={32}
            className="rounded-full"
          />
        </Link>
      </div>
    </nav>
  </header>
);

const FooterComponent: React.FC<{
  data: DesktopData["siteSettings"]["footer"];
}> = ({ data }) => (
  <footer className="bg-white py-24 sm:py-32">
    <div className="mx-auto max-w-7xl px-6 lg:px-8">
      <div className="xl:grid xl:grid-cols-3 xl:gap-8">
        <div className="space-y-8">
          {data?.logo?.logo?.url ? (
            <Image
              className="h-8"
              src={data.logo.logo.url}
              alt={
                getInternationalizedString(data.logo.altText) ||
                data.logo.logo.altText ||
                getInternationalizedString(data.logo.name) ||
                "Company logo"
              }
              width={32}
              height={32}
            />
          ) : (
            <span className="text-lg font-bold text-gray-900">Untitled UI</span>
          )}
          <p className="text-sm leading-6 text-gray-600">
            © 2077 Untitled UI. All rights reserved.
          </p>
        </div>
        <div className="mt-16 grid grid-cols-2 gap-8 xl:col-span-2 xl:mt-0">
          {data?.linkColumns
            ?.filter((column) => column !== null)
            ?.map((column, colIdx) => (
              <div key={colIdx} className="md:grid md:grid-cols-2 md:gap-8">
                <div className="mt-10 md:mt-0">
                  <h3 className="text-sm font-semibold leading-6 text-gray-900">
                    {getInternationalizedString(column.title) || "Links"}
                  </h3>
                  <ul role="list" className="mt-6 space-y-4">
                    {column.links
                      ?.filter((link) => link !== null)
                      ?.map((link, linkIdx) => (
                        <li key={linkIdx}>
                          <Link
                            href={getLinkHref(link.link)}
                            className="text-sm leading-6 text-gray-600 hover:text-gray-900"
                          >
                            {getInternationalizedString(link.label) || "Link"}
                          </Link>
                        </li>
                      ))}
                  </ul>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  </footer>
);

interface DesktopProps {
  data: DesktopData;
}

const Desktop: React.FC<DesktopProps> = ({ data }) => {
  if (!data || !data.page) {
    return <div>No page data found.</div>;
  }

  const { page, siteSettings } = data;

  return (
    <div className="bg-white">
      <HeaderComponent data={siteSettings?.header?.logo} />

      <main>
        {page.pageBuilder?.map((section, index) => {
          switch (section._type) {
            case "herosection":
              return (
                <HeroSectionComponent key={`hero-${index}`} data={section} />
              );
            case "socialproofsection":
              return (
                <SocialProofSectionComponent
                  key={`social-${index}`}
                  data={section}
                />
              );
            case "featuressection":
              return (
                <FeaturesSectionComponent
                  key={`features-${index}`}
                  data={section}
                />
              );
            case "quotesection":
              return (
                <QuoteSectionComponent key={`quote-${index}`} data={section} />
              );
            case "metricssection":
              return (
                <MetricsSectionComponent
                  key={`metrics-${index}`}
                  data={section}
                />
              );
            case "ctasection":
              return (
                <CtaSectionComponent key={`cta-${index}`} data={section} />
              );
            default:
              return null;
          }
        })}
      </main>

      <FooterComponent data={siteSettings?.footer} />
    </div>
  );
};

export default Desktop;
