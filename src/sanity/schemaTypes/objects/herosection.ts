import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'herosection',
  title: 'Hero Section',
  type: 'object',
  fields: [
    defineField({
      name: 'headline',
      title: 'Headline',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'tagline',
      title: 'Tagline/Description',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'image',
      title: 'Hero Image',
      type: 'internationalizedArrayImage',
    }),
    defineField({
      name: 'ctaButtons',
      title: 'Call to Action Buttons',
      type: 'array',
      of: [{type: 'button'}],
      validation: (Rule) => Rule.max(2).warning('Consider limiting to one or two buttons for clarity.'),
    }),
  ],
  preview: {
    select: {
      title: 'headline.0.value',
      subtitle: 'tagline.0.value',
      media: 'image.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Hero Section',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})