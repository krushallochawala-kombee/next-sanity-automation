import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'page',
  title: 'Page',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'internationalizedArraySlug',
      options: {
        source: 'title.0.value',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'pageBuilder',
      title: 'Page Sections',
      type: 'array',
      of: [
        {type: 'herosection'},
        {type: 'ctasection'},
        {type: 'featuressection'},
        {type: 'metricssection'},
        {type: 'quotesection'},
        {type: 'socialproofsection'},
      ],
    }),
    defineField({
      name: 'seo',
      title: 'SEO',
      type: 'seo',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
    },
    prepare({title}) {
      return {
        title: title || 'Untitled Page',
      }
    },
  },
})