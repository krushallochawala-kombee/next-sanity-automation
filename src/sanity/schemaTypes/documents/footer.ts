import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footer',
  title: 'Footer',
  type: 'document',
  fields: [
    defineField({
      name: 'footerLogo',
      title: 'Footer Logo',
      type: 'reference',
      to: [{type: 'companylogo'}],
      description: 'The company logo displayed in the footer.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'linkColumns',
      title: 'Link Columns',
      type: 'array',
      of: [{type: 'footerlinkcolumn'}],
      description: 'Organize footer links into multiple columns with headings.',
      validation: (Rule) => Rule.min(1).max(6),
    }),
    defineField({
      name: 'copyrightText',
      title: 'Copyright Text',
      type: 'internationalizedArrayString',
      description: 'The copyright notice displayed at the bottom of the footer.',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      copyright: 'copyrightText.0.value',
      linkColumnsCount: 'linkColumns.length',
    },
    prepare({copyright, linkColumnsCount}) {
      return {
        title: 'Global Footer',
        subtitle: copyright || `${linkColumnsCount || 0} link columns`,
      }
    },
  },
})