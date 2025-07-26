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
        {type: 'footerlink'},
      ],
      validation: (Rule) => Rule.min(1),
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
