import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'companylogo',
  title: 'Company Logo',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Company Name / Alt Text',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
      description: 'The name of the company or descriptive alt text for the logo.',
    }),
    defineField({
      name: 'logo',
      title: 'Logo Image',
      type: 'internationalizedArrayImage',
      validation: (Rule) => Rule.required(),
      description: 'The image file for the company logo.',
    }),
    defineField({
      name: 'url',
      title: 'Link URL (Optional)',
      type: 'internationalizedArrayUrl',
      description: 'The URL this logo links to (e.g., company website).',
    }),
  ],
  preview: {
    select: {
      title: 'name.0.value',
      media: 'logo.0.value.asset',
    },
    prepare({title, media}) {
      return {
        title: title || 'Untitled Company Logo',
        media: media,
      }
    },
  },
})