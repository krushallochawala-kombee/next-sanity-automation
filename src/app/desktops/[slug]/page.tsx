import { getDesktopDataQuery } from "@/components/generated/Desktop/query";
import { createClient } from "next-sanity"; // Using createClient for server-side fetching
import Desktop from "@/components/generated/Desktop/component";
import { DesktopData } from "@/components/generated/Desktop/types";

// Configure your Sanity client
const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  apiVersion: "2023-03-01", // Use a recent API version
  useCdn: process.env.NODE_ENV === "production", // Use CDN in production
});

// Revalidate data every 60 seconds
export const revalidate = 60;

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default async function DesktopPage({ params }: PageProps) {
  const { slug } = await params; // Next.js 15+ requires awaiting params

  // Fetch data using the GROQ query
  const data: DesktopData | null = await client.fetch(getDesktopDataQuery, {
    slug,
  });
  console.log(data);

  if (!data || !data.page) {
    // Handle 404 or no data found
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <p className="text-xl text-gray-700">Page not found.</p>
      </div>
    );
  }

  return <Desktop data={data} />;
}
