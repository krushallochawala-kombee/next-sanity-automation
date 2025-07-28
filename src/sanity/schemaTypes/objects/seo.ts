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
      description: 'The title that appears in search engine results and browser tabs.',
      validation: (Rule) => Rule.max(60).warning('Should be under 60 characters for optimal display.'),
    }),
    defineField({
      name: 'metaDescription',
      title: 'Meta Description',
      type: 'internationalizedArrayText',
      description: 'The description that appears under the meta title in search results.',
      validation: (Rule) => Rule.max(160).warning('Should be under 160 characters for optimal display.'),
    }),
    defineField({
      name: 'ogImage',
      title: 'Open Graph Image',
      type: 'internationalizedArrayImage',
      description: 'Image displayed when sharing on social media. Recommended size: 1200x630px.',
    }),
    defineField({
      name: 'ogTitle',
      title: 'Open Graph Title',
      type: 'internationalizedArrayString',
      description: 'Title for social media sharing (if different from Meta Title).',
    }),
    defineField({
      name: 'ogDescription',
      title: 'Open Graph Description',
      type: 'internationalizedArrayText',
      description: 'Description for social media sharing (if different from Meta Description).',
    }),
    defineField({
      name: 'keywords',
      title: 'Keywords',
      type: 'array',
      description: 'Comma-separated keywords for search engines (optional, less critical now).',
      of: [{type: 'internationalizedArrayString'}],
    }),
    defineField({
      name: 'noIndex',
      title: 'No Index',
      type: 'boolean',
      description: 'If checked, search engines will be discouraged from indexing this page.',
      initialValue: false,
    }),
    defineField({
      name: 'canonicalUrl',
      title: 'Canonical URL',
      type: 'internationalizedArrayUrl',
      description: 'Specify a canonical URL if this page has duplicate content elsewhere.',
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
        title: title || 'SEO Settings',
        subtitle: subtitle || 'No meta description set',
        media: media,
      }
    },
  },
})