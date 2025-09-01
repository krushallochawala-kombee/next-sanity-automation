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
        {type: 'badge'},
        {type: 'button'},
        {type: 'ctasection'},
        {type: 'featuressection'},
        {type: 'footerlink'},
        {type: 'footerlinkcolumn'},
        {type: 'herosection'},
        {type: 'imagewithalt'},
        {type: 'link'},
        {type: 'metricssection'},
        {type: 'quotesection'},
        {type: 'seo'}, // Note: This refers to the 'seo' object type, not the document.
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
      slug: 'slug.0.current',
      media: 'seo.ogImage.0.value.asset',
    },
    prepare({title, slug, media}) {
      return {
        title: title || 'Untitled Page',
        subtitle: slug ? `/${slug}` : 'No slug set',
        media: media,
      }
    },
  },
})