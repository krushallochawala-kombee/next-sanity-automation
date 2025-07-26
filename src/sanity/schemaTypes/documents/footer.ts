import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footer',
  title: 'Footer',
  type: 'document',
  fields: [
    defineField({
      name: 'linkColumns',
      title: 'Link Columns',
      description: 'The columns of links displayed in the footer.',
      type: 'array',
      of: [{type: 'footerlinkcolumn'}],
      validation: (Rule) => Rule.required().min(1),
    }),
    defineField({
      name: 'companyLogo',
      title: 'Company Logo',
      description: 'The logo displayed at the bottom of the footer.',
      type: 'reference',
      to: [{type: 'companylogo'}],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'copyrightText',
      title: 'Copyright Text',
      description: 'The copyright text displayed at the bottom of the footer.',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
  ],
})