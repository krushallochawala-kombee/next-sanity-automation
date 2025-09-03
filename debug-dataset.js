const { createClient } = require('next-sanity');
require('dotenv').config({ path: '.env.local' });

const client = createClient({
    projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
    apiVersion: '2023-03-01',
    useCdn: false,
});

async function debugDataset() {
    console.log('🔍 Debugging your Sanity dataset...');
    console.log(`Project ID: ${process.env.NEXT_PUBLIC_SANITY_PROJECT_ID}`);
    console.log(`Dataset: ${process.env.NEXT_PUBLIC_SANITY_DATASET}`);

    try {
        // Check what document types exist
        console.log('\n📋 Checking available document types...');
        const documentTypes = await client.fetch(`array::unique(*[_type in ["page", "siteSettings", "footer", "companylogo", "feature", "metricitem"]]._type)`);
        console.log('Available document types:', documentTypes);

        // Check if there are any pages
        console.log('\n📄 Checking for pages...');
        const pageCount = await client.fetch(`count(*[_type == "page"])`);
        console.log(`Total pages: ${pageCount}`);

        if (pageCount > 0) {
            // Get a sample page
            const samplePage = await client.fetch(`*[_type == "page"][0] {
        _id,
        _type,
        title,
        slug,
        "hasPageBuilder": defined(pageBuilder)
      }`);
            console.log('Sample page:', JSON.stringify(samplePage, null, 2));
        }

        // Check site settings
        console.log('\n⚙️ Checking site settings...');
        const siteSettingsCount = await client.fetch(`count(*[_type == "siteSettings"])`);
        console.log(`Site settings documents: ${siteSettingsCount}`);

        if (siteSettingsCount > 0) {
            const siteSettings = await client.fetch(`*[_type == "siteSettings"][0] {
        _id,
        _type,
        siteName,
        siteDescription
      }`);
            console.log('Site settings:', JSON.stringify(siteSettings, null, 2));
        }

        // Check all documents
        console.log('\n📊 All documents in dataset:');
        const allDocs = await client.fetch(`*[_type in ["page", "siteSettings", "footer", "companylogo", "feature", "metricitem"]] {
      _id,
      _type,
      _createdAt
    } | order(_createdAt desc)`);
        console.log(JSON.stringify(allDocs, null, 2));

        if (allDocs.length === 0) {
            console.log('\n❌ No documents found! You need to create some content in your Sanity Studio first.');
            console.log('💡 Go to your Sanity Studio and create:');
            console.log('   1. A "Page" document with a slug');
            console.log('   2. A "Site Settings" document');
            console.log('   3. Some content in the pageBuilder array');
        }

    } catch (error) {
        console.error('❌ Error debugging dataset:', error.message);
    }
}

debugDataset().catch(console.error);

