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
      console.log(`\n📋 Testing: ${name}`);
      console.log('Query:', query);
      const result = await client.fetch(query);
      console.log('✅ Result:', JSON.stringify(result, null, 2));
    } catch (error) {
      console.error(`❌ Error in ${name}:`, error.message);
    }
  }
}

testGroqQueries().catch(console.error);