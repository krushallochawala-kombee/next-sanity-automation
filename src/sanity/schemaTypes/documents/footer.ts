import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footer',
  title: 'Footer',
  type: 'document',
  fields: [
    defineField({
      name: 'columns',
      title: 'Link Columns',
      type: 'array',
      description: 'The columns of links displayed in the footer.',
      of: [
        {type: 'footerlinkcolumn'}
      ],
      validation: (Rule) => Rule.required().min(1),
    }),
    defineField({
      name: 'logo',
      title: 'Company Logo',
      type: 'reference',
      to: [{type: 'companylogo'}],
      description: 'The company logo displayed in the footer.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'copyrightText',
      title: 'Copyright Text',
      type: 'internationalizedArrayString',
      description: 'The copyright text displayed at the bottom of the footer.',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      copyright: 'copyrightText.0.value',
      numColumns: 'columns.length',
    },
    prepare({copyright, numColumns}) {
      const columnsSubtitle = numColumns ? `${numColumns} link columns` : 'No link columns';
      return {
        title: copyright || 'Untitled Footer',
        subtitle: columnsSubtitle,
      }
    },
  },
})