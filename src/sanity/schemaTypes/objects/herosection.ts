import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'herosection',
  title: 'Hero Section',
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
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'image',
      title: 'Hero Image',
      type: 'internationalizedArrayImage',
      options: {
        hotspot: true,
      },
    }),
    defineField({
      name: 'ctaButtons',
      title: 'Call to Action Buttons',
      type: 'array',
      of: [{type: 'button'}],
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
        title: title || 'Untitled Hero Section',
        subtitle: subtitle || 'No tagline',
        media: media,
      }
    },
  },
})