import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'header',
  title: 'Header',
  type: 'document',
  fields: [
    defineField({
      name: 'logo',
      title: 'Logo',
      type: 'logo',
      description: 'The main site logo, typically linking to the homepage.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'navigation',
      title: 'Navigation Links',
      type: 'array',
      description: 'Links for the main navigation menu.',
      of: [{type: 'navigationlink'}],
    }),
    defineField({
      name: 'callToAction',
      title: 'Call to Action Button',
      type: 'button',
      description: 'Optional call to action button in the header.',
    }),
  ],
  preview: {
    select: {
      title: 'logo.alt.0.value', // Assumes 'logo' object has an i18n 'alt' field
      media: 'logo.image.0.value.asset', // Assumes 'logo' object has an i18n 'image' field
    },
    prepare({title, media}) {
      return {
        title: 'Site Header', // Fixed title for a singleton document
        subtitle: title ? `Logo: ${title}` : 'No logo alt text',
        media: media,
      }
    },
  },
})