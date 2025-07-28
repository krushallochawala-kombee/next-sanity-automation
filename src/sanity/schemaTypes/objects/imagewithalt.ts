import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'imagewithalt',
  title: 'Image with Alt Text',
  type: 'object',
  fields: [
    defineField({
      name: 'image',
      title: 'Image',
      type: 'internationalizedArrayImage',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'altText',
      title: 'Alternative Text',
      type: 'internationalizedArrayString',
      description: 'Important for SEO and accessibility. Describe the image content.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'caption',
      title: 'Caption',
      type: 'internationalizedArrayText',
      description: 'Optional text displayed below the image.',
    }),
  ],
  preview: {
    select: {
      title: 'altText.0.value',
      subtitle: 'caption.0.value',
      media: 'image.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Image (No Alt Text)',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})