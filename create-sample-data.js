const { createClient } = require('next-sanity');
require('dotenv').config({ path: '.env.local' });

const client = createClient({
    projectId: process.env.NEXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NEXT_PUBLIC_SANITY_DATASET,
    apiVersion: '2023-03-01',
    useCdn: false,
    token: process.env.SANITY_API_TOKEN, // You'll need to add this to your .env.local
});

async function createSampleData() {
    console.log('🚀 Creating sample data for your Sanity dataset...');

    try {
        // 1. Create Site Settings
        console.log('\n📝 Creating Site Settings...');
        const siteSettings = await client.create({
            _type: 'siteSettings',
            siteName: [
                {
                    _key: 'en',
                    _type: 'internationalizedArrayStringValue',
                    value: 'My Awesome Website'
                }
            ],
            siteDescription: [
                {
                    _key: 'en',
                    _type: 'internationalizedArrayTextValue',
                    value: 'A modern website built with Next.js and Sanity CMS'
                }
            ]
        });
        console.log('✅ Site Settings created:', siteSettings._id);

        // 2. Create Company Logos
        console.log('\n🏢 Creating Company Logos...');
        const logos = [];
        const companyNames = ['Acme Corp', 'Tech Solutions', 'Digital Agency', 'Innovation Labs'];

        for (const name of companyNames) {
            const logo = await client.create({
                _type: 'companylogo',
                name: [
                    {
                        _key: 'en',
                        _type: 'internationalizedArrayStringValue',
                        value: name
                    }
                ],
                altText: [
                    {
                        _key: 'en',
                        _type: 'internationalizedArrayStringValue',
                        value: `${name} logo`
                    }
                ]
            });
            logos.push(logo);
            console.log(`✅ Logo created: ${name} (${logo._id})`);
        }

        // 3. Create Features
        console.log('\n⭐ Creating Features...');
        const features = [];
        const featureData = [
            { title: 'Fast Performance', description: 'Lightning-fast loading times' },
            { title: 'Mobile Responsive', description: 'Works perfectly on all devices' },
            { title: 'SEO Optimized', description: 'Built for search engine visibility' },
            { title: 'Easy to Use', description: 'Intuitive user experience' }
        ];

        for (const feature of featureData) {
            const featureDoc = await client.create({
                _type: 'feature',
                title: [
                    {
                        _key: 'en',
                        _type: 'internationalizedArrayStringValue',
                        value: feature.title
                    }
                ],
                description: [
                    {
                        _key: 'en',
                        _type: 'internationalizedArrayTextValue',
                        value: feature.description
                    }
                ]
            });
            features.push(featureDoc);
            console.log(`✅ Feature created: ${feature.title} (${featureDoc._id})`);
        }

        // 4. Create Metric Items
        console.log('\n📊 Creating Metric Items...');
        const metrics = [];
        const metricData = [
            { value: '10K+', label: 'Happy Customers' },
            { value: '99.9%', label: 'Uptime' },
            { value: '24/7', label: 'Support' },
            { value: '5★', label: 'Rating' }
        ];

        for (const metric of metricData) {
            const metricDoc = await client.create({
                _type: 'metricitem',
                value: [
                    {
                        _key: 'en',
                        _type: 'internationalizedArrayStringValue',
                        value: metric.value
                    }
                ],
                label: [
                    {
                        _key: 'en',
                        _type: 'internationalizedArrayTextValue',
                        value: metric.label
                    }
                ]
            });
            metrics.push(metricDoc);
            console.log(`✅ Metric created: ${metric.value} ${metric.label} (${metricDoc._id})`);
        }

        // 5. Create Footer
        console.log('\n🦶 Creating Footer...');
        const footer = await client.create({
            _type: 'footer',
            linkColumns: [
                {
                    _key: 'company',
                    _type: 'footerlinkscolumn',
                    title: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayStringValue',
                            value: 'Company'
                        }
                    ],
                    links: [
                        {
                            _key: 'about',
                            _type: 'footerlink',
                            label: [
                                {
                                    _key: 'en',
                                    _type: 'internationalizedArrayStringValue',
                                    value: 'About Us'
                                }
                            ],
                            link: {
                                _type: 'link',
                                externalUrl: [
                                    {
                                        _key: 'en',
                                        _type: 'internationalizedArrayUrlValue',
                                        value: '/about'
                                    }
                                ]
                            }
                        }
                    ]
                }
            ],
            copyrightText: [
                {
                    _key: 'en',
                    _type: 'internationalizedArrayTextValue',
                    value: '© 2024 My Awesome Website. All rights reserved.'
                }
            ]
        });
        console.log('✅ Footer created:', footer._id);

        // 6. Create a Page with PageBuilder content
        console.log('\n📄 Creating Page with PageBuilder...');
        const page = await client.create({
            _type: 'page',
            title: [
                {
                    _key: 'en',
                    _type: 'internationalizedArrayStringValue',
                    value: 'Welcome to Our Website'
                }
            ],
            slug: [
                {
                    _key: 'en',
                    _type: 'internationalizedArraySlugValue',
                    value: {
                        _type: 'slug',
                        current: 'welcome'
                    }
                }
            ],
            pageBuilder: [
                {
                    _key: 'hero',
                    _type: 'herosection',
                    headline: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayStringValue',
                            value: 'Build Amazing Websites'
                        }
                    ],
                    tagline: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayTextValue',
                            value: 'Create stunning, responsive websites with our modern tools and technologies.'
                        }
                    ],
                    ctaButtons: [
                        {
                            _key: 'cta1',
                            _type: 'button',
                            label: [
                                {
                                    _key: 'en',
                                    _type: 'internationalizedArrayStringValue',
                                    value: 'Get Started'
                                }
                            ],
                            link: {
                                _type: 'link',
                                externalUrl: [
                                    {
                                        _key: 'en',
                                        _type: 'internationalizedArrayUrlValue',
                                        value: '/get-started'
                                    }
                                ]
                            }
                        }
                    ]
                },
                {
                    _key: 'features',
                    _type: 'featuressection',
                    title: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayStringValue',
                            value: 'Why Choose Us?'
                        }
                    ],
                    description: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayTextValue',
                            value: 'We provide the best tools and services for your web development needs.'
                        }
                    ],
                    features: features.map(f => ({ _ref: f._id, _type: 'reference' }))
                },
                {
                    _key: 'socialproof',
                    _type: 'socialproofsection',
                    title: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayStringValue',
                            value: 'Trusted by Leading Companies'
                        }
                    ],
                    description: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayTextValue',
                            value: 'Join thousands of satisfied customers who trust our platform.'
                        }
                    ],
                    logos: logos.map(l => ({ _ref: l._id, _type: 'reference' }))
                },
                {
                    _key: 'metrics',
                    _type: 'metricssection',
                    title: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayStringValue',
                            value: 'Our Success in Numbers'
                        }
                    ],
                    description: [
                        {
                            _key: 'en',
                            _type: 'internationalizedArrayTextValue',
                            value: 'See how we\'re making a difference in the industry.'
                        }
                    ],
                    metrics: metrics.map(m => ({
                        _key: m._id,
                        _type: 'metricitem',
                        value: m.value,
                        label: m.label
                    }))
                }
            ]
        });
        console.log('✅ Page created:', page._id);

        console.log('\n🎉 Sample data creation complete!');
        console.log('\n📋 Summary:');
        console.log(`   - Site Settings: ${siteSettings._id}`);
        console.log(`   - Company Logos: ${logos.length} created`);
        console.log(`   - Features: ${features.length} created`);
        console.log(`   - Metrics: ${metrics.length} created`);
        console.log(`   - Footer: ${footer._id}`);
        console.log(`   - Page: ${page._id}`);

        console.log('\n🧪 Now you can test your GROQ queries:');
        console.log('   node test-groq.js');
        console.log('\n🚀 And run your UI generator:');
        console.log('   python ui-generator.py');

    } catch (error) {
        console.error('❌ Error creating sample data:', error.message);
        if (error.message.includes('token')) {
            console.log('\n💡 You need to add SANITY_API_TOKEN to your .env.local file');
            console.log('   Get your token from: https://sanity.io/manage');
        }
    }
}

createSampleData().catch(console.error);

