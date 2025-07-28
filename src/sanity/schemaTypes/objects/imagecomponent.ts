import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'imagecomponent',
  title: 'Image Component',
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
      type: 'internationalizedArrayString',
      description: 'Important for SEO and accessibility. Describe the image content concisely.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'caption',
      title: 'Caption',
      type: 'internationalizedArrayText',
      description: 'Optional caption displayed below the image.',
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
        title: title || 'Untitled Image Component',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})