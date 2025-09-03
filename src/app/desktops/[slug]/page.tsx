import { client } from '@/sanity/lib/client';
import { getDesktopDataQuery } from '@/components/generated/Desktop/query';
import Desktop from '@/components/generated/Desktop/component';
import { notFound } from 'next/navigation';
import type { DesktopData } from '@/components/generated/Desktop/types';

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function DesktopPage({ params }: PageProps) {
  const { slug } = await params; // CRITICAL: await params in Next.js 15+

  const data: DesktopData | null = await client.fetch(getDesktopDataQuery, { slug });

  if (!data || !data.page) {
    notFound();
  }

  return <Desktop data={data} />;
}