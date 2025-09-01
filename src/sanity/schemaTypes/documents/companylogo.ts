import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'companylogo',
  title: 'Company Logo',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Company Name',
      type: 'internationalizedArrayString',
      description: 'The name of the company for accessibility and internal use.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'logo',
      title: 'Logo Image',
      type: 'internationalizedArrayImage',
      options: {
        hotspot: true,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'Company Website URL',
      type: 'internationalizedArrayUrl',
      description: 'Optional: Link to the company\'s website when clicking the logo.',
    }),
  ],
  preview: {
    select: {
      title: 'name.0.value',
      subtitle: 'url.0.value',
      media: 'logo.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Company Logo',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})
