import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footer',
  title: 'Footer',
  type: 'document',
  fields: [
    defineField({
      name: 'linkColumns',
      title: 'Link Columns',
      type: 'array',
      description: 'The columns of links displayed in the footer. Use existing "Footer links column" objects.',
      of: [{type: 'footerlinkscolumn'}],
      validation: (Rule) => Rule.min(1).error('At least one link column is required.'),
    }),
    defineField({
      name: 'logo',
      title: 'Company Logo',
      type: 'reference',
      to: [{type: 'companylogo'}],
      description: 'The company logo to display in the footer.',
    }),
    defineField({
      name: 'copyrightText',
      title: 'Copyright Text',
      type: 'internationalizedArrayText',
      description: 'The copyright text (e.g., © 2023 Your Company. All rights reserved.).',
      validation: (Rule) => Rule.required().error('Copyright text is required.'),
    }),
  ],
  preview: {
    select: {
      copyright: 'copyrightText.0.value',
      logoAsset: 'logo->image.0.value.asset', // Access asset from the referenced companylogo document
      linkColumnCount: 'linkColumns.length',
    },
    prepare({copyright, logoAsset, linkColumnCount}) {
      const subtitle = copyright
        ? copyright
        : linkColumnCount > 0
          ? `${linkColumnCount} link columns`
          : 'No content configured';

      return {
        title: 'Global Footer',
        subtitle: subtitle,
        media: logoAsset,
      }
    },
  },
})