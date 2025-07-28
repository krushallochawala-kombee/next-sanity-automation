import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footerlinkscolumn',
  title: 'Footer Links Column',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Column Title',
      type: 'internationalizedArrayString',
      description: 'The title for this column of links (e.g., "Company", "Products").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'links',
      title: 'Links',
      type: 'array',
      description: 'The list of individual links in this column.',
      of: [
        {type: 'link'} // 'link' is an available object for embedding.
      ],
      validation: (Rule) => Rule.required().min(1),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      linkCount: 'links.length',
    },
    prepare({title, linkCount}) {
      const subtitleText = linkCount ? `${linkCount} link${linkCount === 1 ? '' : 's'}` : 'No links defined';
      return {
        title: title || 'Untitled Footer Column',
        subtitle: subtitleText,
      }
    },
  },
})
