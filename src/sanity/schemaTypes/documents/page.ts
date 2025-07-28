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
      description: 'Add and reorder sections for your page.',
      of: [
        {type: 'author'},
        {type: 'button'},
        {type: 'ctasection'},
        {type: 'featuressection'},
        {type: 'footerlink'},
        {type: 'footerlinkscolumn'},
        {type: 'herosection'},
        {type: 'imagewithalt'},
        {type: 'link'},
        {type: 'metricssection'},
        {type: 'quotesection'},
        {type: 'seo'}, // Note: This is a standalone object in the list, though usually embedded. Following strict instruction.
        {type: 'socialproofsection'},
      ],
    }),
    defineField({
      name: 'seo',
      title: 'SEO',
      type: 'seo',
      description: 'Search Engine Optimization metadata.',
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'slug.0.value.current',
      media: 'seo.ogImage.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Page',
        subtitle: subtitle ? `/${subtitle}` : 'No slug set',
        media: media,
      }
    },
  },
})