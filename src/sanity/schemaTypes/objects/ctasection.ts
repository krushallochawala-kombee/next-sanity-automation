import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'ctasection',
  title: 'CTA Section',
  type: 'object',
  fields: [
    defineField({
      name: 'heading',
      title: 'Heading',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'tagline',
      title: 'Tagline',
      description: 'A short descriptive text for the CTA.',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'button',
      title: 'Call to Action Button',
      type: 'button', // Referencing the 'button' object type
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'image',
      title: 'Background Image',
      type: 'internationalizedArrayImage',
      description: 'Optional background image for the CTA section.',
    }),
  ],
  preview: {
    select: {
      title: 'heading.0.value',
      subtitle: 'tagline.0.value',
      media: 'image.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled CTA Section',
        subtitle: subtitle || 'Call to Action Section',
        media: media,
      }
    },
  },
})