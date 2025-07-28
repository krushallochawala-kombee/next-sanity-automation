import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footerlinkcolumn',
  title: 'Footer Link Column',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Column Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'links',
      title: 'Links',
      type: 'array',
      of: [
        {
          name: 'internalLink',
          title: 'Internal Link',
          type: 'object',
          fields: [
            defineField({
              name: 'label',
              title: 'Link Label',
              type: 'internationalizedArrayString',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'reference',
              title: 'Page Reference',
              type: 'reference',
              to: [{type: 'page'}],
              validation: (Rule) => Rule.required(),
            }),
          ],
          preview: {
            select: {
              title: 'label.0.value',
              subtitle: 'reference._ref',
            },
            prepare({title, subtitle}) {
              return {
                title: title || 'Untitled Internal Link',
                subtitle: `Internal: ${subtitle}`,
              }
            },
          },
        },
        {
          name: 'externalLink',
          title: 'External Link',
          type: 'object',
          fields: [
            defineField({
              name: 'label',
              title: 'Link Label',
              type: 'internationalizedArrayString',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'url',
              title: 'URL',
              type: 'internationalizedArrayUrl',
              validation: (Rule) => Rule.required(),
            }),
          ],
          preview: {
            select: {
              title: 'label.0.value',
              subtitle: 'url.0.value',
            },
            prepare({title, subtitle}) {
              return {
                title: title || 'Untitled External Link',
                subtitle: `External: ${subtitle}`,
              }
            },
          },
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      linkCount: 'links.length',
    },
    prepare({title, linkCount}) {
      return {
        title: title || 'Untitled Footer Column',
        subtitle: `${linkCount || 0} link(s)`,
      }
    },
  },
})