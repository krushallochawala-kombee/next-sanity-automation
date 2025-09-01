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
      validation: (Rule) => Rule.required().max(60).warning('Meta Title should be 60 characters or less.'),
      description: 'The title displayed in search engine results and browser tabs (max 60 characters).',
    }),
    defineField({
      name: 'metaDescription',
      title: 'Meta Description',
      type: 'internationalizedArrayText',
      validation: (Rule) => Rule.required().max(160).warning('Meta Description should be 160 characters or less.'),
      description: 'The description displayed in search engine results (max 160 characters).',
    }),
    defineField({
      name: 'ogImage',
      title: 'Open Graph Image',
      type: 'internationalizedArrayImage',
      description: 'Image displayed when sharing on social media (e.g., Facebook, Twitter).',
    }),
    defineField({
      name: 'ogTitle',
      title: 'Open Graph Title',
      type: 'internationalizedArrayString',
      description: 'Title displayed when sharing on social media. If empty, Meta Title will be used.',
    }),
    defineField({
      name: 'ogDescription',
      title: 'Open Graph Description',
      type: 'internationalizedArrayText',
      description: 'Description displayed when sharing on social media. If empty, Meta Description will be used.',
    }),
    defineField({
      name: 'keywords',
      title: 'Keywords',
      type: 'array',
      of: [{type: 'internationalizedArrayString'}],
      description: 'Comma-separated keywords for search engines (less critical for ranking, but still useful).',
    }),
    defineField({
      name: 'noIndex',
      title: 'No Index',
      type: 'boolean',
      description: 'If true, search engines will be instructed not to index this page.',
      initialValue: false,
    }),
    defineField({
      name: 'canonicalUrl',
      title: 'Canonical URL',
      type: 'internationalizedArrayUrl',
      description: 'The preferred URL for this page, to prevent duplicate content issues.',
    }),
  ],
  preview: {
    select: {
      title: 'metaTitle.0.value',
      subtitle: 'metaDescription.0.value',
      media: 'ogImage.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled SEO Configuration',
        subtitle: subtitle || 'No description set',
        media: media,
      }
    },
  },
})