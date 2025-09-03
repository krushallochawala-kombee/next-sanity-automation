const { createClient } = require('next-sanity');
require('dotenv').config({ path: '.env.local' });

const client = createClient({
  projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
  dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
  apiVersion: '2023-03-01',
  useCdn: false,
});

async function analyzeSchema() {
  console.log('🔍 Analyzing schema structure...');
  
  try {
    // Check a sample page to understand structure
    const samplePage = await client.fetch(`*[_type == "page"][0] {
      title,
      slug,
      "titleType": title._type,
      "slugType": slug._type,
      "titleIsArray": title[0]._type,
      "slugIsArray": slug[0]._type
    }`);
    
    console.log('📄 Sample page structure:');
    console.log(JSON.stringify(samplePage, null, 2));
    
    // Determine if using internationalized arrays
    const isInternationalized = Array.isArray(samplePage?.title) && 
      samplePage.title[0]?._type?.includes('internationalized');
    
    console.log('\n🌐 Schema type:', isInternationalized ? 'INTERNATIONALIZED ARRAYS' : 'STANDARD FIELDS');
    
    if (isInternationalized) {
      console.log('✅ Use: slug[0].value.current for filtering');
      console.log('✅ Use: getInternationalizedString() helpers in components');
      console.log('✅ Use: field { value { asset->{url, altText} } } for images');
      console.log('✅ Use: just "field" for text fields in GROQ');
    } else {
      console.log('✅ Use: slug.current for filtering');
      console.log('✅ Use: PortableText components for rich text');
    }
    
    // Test a simple query
    console.log('\n🧪 Testing GROQ query...');
    const testQuery = isInternationalized 
      ? `*[_type == "page" && slug[0].value.current == "test"][0] { title, slug }`
      : `*[_type == "page" && slug.current == "test"][0] { title, slug }`;
    
    console.log('Test query:', testQuery);
    
  } catch (error) {
    console.error('❌ Error analyzing schema:', error);
  }
}

analyzeSchema().catch(console.error);