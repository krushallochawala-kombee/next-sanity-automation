import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'seo',
  title: 'SEO',
  type: 'object',
  fields: [
    defineField({
      name: 'metaTitle',
      title: 'Meta Title',
      type: 'internationalizedArrayString',
      description: 'The title displayed in search engine results and browser tabs (max 60 characters).',
      validation: (Rule) => Rule.max(60).warning('Meta title should ideally be under 60 characters.'),
    }),
    defineField({
      name: 'metaDescription',
      title: 'Meta Description',
      type: 'internationalizedArrayText',
      description: 'The description displayed in search engine results (max 160 characters).',
      validation: (Rule) => Rule.max(160).warning('Meta description should ideally be under 160 characters.'),
    }),
    defineField({
      name: 'ogImage',
      title: 'Open Graph Image',
      type: 'internationalizedArrayImage',
      description: 'Image displayed when shared on social media (e.g., Facebook, Twitter). Optimal size: 1200x630px.',
    }),
    defineField({
      name: 'ogTitle',
      title: 'Open Graph Title',
      type: 'internationalizedArrayString',
      description: 'Title displayed when shared on social media. If empty, uses Meta Title.',
    }),
    defineField({
      name: 'ogDescription',
      title: 'Open Graph Description',
      type: 'internationalizedArrayText',
      description: 'Description displayed when shared on social media. If empty, uses Meta Description.',
    }),
    defineField({
      name: 'keywords',
      title: 'Keywords',
      type: 'array',
      of: [{type: 'internationalizedArrayString'}],
      description: 'Comma-separated keywords relevant to the page content (optional for SEO, but can be useful for internal search).',
    }),
    defineField({
      name: 'noIndex',
      title: 'No Index',
      type: 'boolean',
      description: 'Check this box to prevent search engines from indexing this page.',
      initialValue: false,
    }),
    defineField({
      name: 'canonicalUrl',
      title: 'Canonical URL',
      type: 'internationalizedArrayUrl',
      description: 'The preferred URL for this page to prevent duplicate content issues. Leave empty to auto-generate from slug.',
    }),
  ],
})