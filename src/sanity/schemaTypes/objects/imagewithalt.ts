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
      title: 'Alt Text',
      description: 'Important for accessibility and SEO. Describe the image content concisely.',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'caption',
      title: 'Caption',
      description: 'Optional caption for the image.',
      type: 'internationalizedArrayText',
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