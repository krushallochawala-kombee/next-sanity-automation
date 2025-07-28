import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'companylogo',
  title: 'Company Logo',
  type: 'document',
  fields: [
    defineField({
      name: 'name',
      title: 'Company Name',
      description: 'The name of the company for this logo.',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'logo',
      title: 'Logo Image',
      type: 'internationalizedArrayImage',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'altText',
      title: 'Alt Text for Logo',
      description: 'Important for accessibility and SEO (e.g., "Acme Corp Logo").',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'Link URL (Optional)',
      description: 'The URL this logo should link to, if any.',
      type: 'internationalizedArrayUrl',
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
        subtitle: subtitle ? `Links to: ${subtitle}` : 'No URL set',
        media: media,
      }
    },
  },
})