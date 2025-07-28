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
      description: 'The main heading for the social proof section.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      description: 'An optional subtitle or descriptive text for the section.',
    }),
    defineField({
      name: 'logos',
      title: 'Company Logos',
      type: 'array',
      description: 'A list of company logos to display.',
      of: [
        {type: 'reference', to: [{type: 'companylogo'}]},
      ],
      validation: (Rule) => Rule.required().min(1).error('At least one logo is required for social proof.'),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'description.0.value',
      // Media is not directly available on this object type, so we omit it for simplicity.
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Social Proof Section',
        subtitle: subtitle || 'No description provided',
      }
    },
  },
})