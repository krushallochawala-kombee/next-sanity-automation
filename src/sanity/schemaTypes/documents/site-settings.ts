import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'siteSettings',
  title: 'Site Settings',
  type: 'document',
  fields: [
    defineField({
      name: 'siteName',
      title: 'Site Name',
      type: 'internationalizedArrayString',
      description: 'The global name of the website.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'header',
      title: 'Global Header',
      type: 'reference',
      to: [{type: 'header'}],
      description: 'Reference to the global header document.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'footer',
      title: 'Global Footer',
      type: 'reference',
      to: [{type: 'footer'}],
      description: 'Reference to the global footer document.',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      siteName: 'siteName.0.value',
    },
    prepare({siteName}) {
      return {
        title: 'Site Settings',
        subtitle: siteName || 'Global Settings',
      }
    },
  },
})