import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'quotesection',
  title: 'Quote Section',
  type: 'object',
  fields: [
    defineField({
      name: 'quote',
      title: 'Quote Text',
      type: 'internationalizedArrayText',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'authorName',
      title: 'Author Name',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'authorTitle',
      title: 'Author Title/Position',
      type: 'internationalizedArrayString',
    }),
    defineField({
      name: 'authorImage',
      title: 'Author Image',
      type: 'internationalizedArrayImage',
    }),
  ],
  preview: {
    select: {
      title: 'quote.0.value',
      subtitle: 'authorName.0.value',
      media: 'authorImage.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Quote Section',
        subtitle: subtitle ? `by ${subtitle}` : 'No Author',
        media: media,
      }
    },
  },
})