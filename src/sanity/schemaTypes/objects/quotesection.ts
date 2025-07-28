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
      name: 'attribution',
      title: 'Attribution',
      description: 'The person or entity the quote is attributed to.',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source',
      title: 'Source (Optional)',
      description: 'Additional context for the attribution (e.g., "CEO of Company X", "Their Website").',
      type: 'internationalizedArrayString',
    }),
  ],
  preview: {
    select: {
      title: 'quote.0.value',
      subtitle: 'attribution.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled Quote Section',
        subtitle: subtitle ? `— ${subtitle}` : '',
      }
    },
  },
})