import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'quotesection',
  title: 'Quote Section',
  type: 'object',
  fields: [
    defineField({
      name: 'quote',
      title: 'Quote',
      type: 'internationalizedArrayText',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'attribution',
      title: 'Attribution',
      type: 'internationalizedArrayString',
      description: 'Who said the quote (e.g., "John Doe, CEO")',
    }),
  ],
  preview: {
    select: {
      quote: 'quote.0.value',
      attribution: 'attribution.0.value',
    },
    prepare({quote, attribution}) {
      return {
        title: quote ? `"${quote}"` : 'Untitled Quote Section',
        subtitle: attribution ? `— ${attribution}` : 'No Attribution',
      }
    },
  },
})