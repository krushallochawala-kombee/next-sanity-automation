import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'siteSettings',
  title: 'Site Settings',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Site Title',
      type: 'internationalizedArrayString',
      description: 'The main title for the website.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'header',
      title: 'Header',
      type: 'reference',
      to: [{type: 'header'}],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'footer',
      title: 'Footer',
      type: 'reference',
      to: [{type: 'footer'}],
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
    },
    prepare({title}) {
      return {
        title: title || 'Site Settings',
        subtitle: 'Global Site Configuration',
      }
    },
  },
})