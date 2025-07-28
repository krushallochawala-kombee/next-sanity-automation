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
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      description: 'Used for SEO and social sharing descriptions.',
    }),
    defineField({
      name: 'pageBuilder',
      title: 'Page Sections',
      type: 'array',
      description: 'Add and arrange sections for this page.',
      of: [
        {type: 'herosection'},
        {type: 'featuressection'},
        {type: 'ctasection'},
        {type: 'quotesection'},
        {type: 'metricssection'},
        {type: 'socialproofsection'},
        {type: 'imagecomponent'},
        {type: 'textblock'},
      ],
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'slug.0.current',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled Page',
        subtitle: subtitle ? `/${subtitle}` : 'No slug set',
      }
    },
  },
})