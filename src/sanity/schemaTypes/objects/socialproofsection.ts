import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'socialproofsection',
  title: 'Social Proof Section',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'proofItems',
      title: 'Proof Items',
      type: 'array',
      description: 'Add quotes/testimonials or company logos to showcase social proof.',
      of: [
        {
          type: 'reference',
          name: 'quoteReference',
          title: 'Quote/Testimonial',
          to: [{type: 'quotesection'}],
        },
        {
          type: 'reference',
          name: 'companyLogoReference',
          title: 'Company Logo',
          to: [{type: 'companylogo'}],
        },
      ],
      validation: (Rule) => Rule.min(1).required(),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'description.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Social Proof Section',
        subtitle: subtitle || 'Displays testimonials or client logos',
      }
    },
  },
})