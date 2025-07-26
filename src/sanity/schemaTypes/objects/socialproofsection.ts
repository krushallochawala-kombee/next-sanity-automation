import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'socialproofsection',
  title: 'Social Proof Section',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Section Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'quotes',
      title: 'Testimonial Quotes',
      type: 'array',
      of: [
        {
          name: 'quoteItem',
          type: 'object',
          fields: [
            defineField({
              name: 'quote',
              title: 'Quote Text',
              type: 'internationalizedArrayText',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'author',
              title: 'Author Name',
              type: 'internationalizedArrayString',
            }),
          ],
          preview: {
            select: {
              title: 'quote.0.value',
              subtitle: 'author.0.value',
            },
            prepare({title, subtitle}) {
              return {
                title: title || 'Untitled Quote',
                subtitle: subtitle,
              }
            },
          },
        },
      ],
    }),
    defineField({
      name: 'logos',
      title: 'Company Logos',
      type: 'array',
      of: [{type: 'logo'}],
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
    },
    prepare({title}) {
      return {
        title: title || 'Social Proof Section',
      }
    },
  },
})