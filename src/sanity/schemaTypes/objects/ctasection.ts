import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'ctasection',
  title: 'Call to Action Section',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'image',
      title: 'Image',
      type: 'internationalizedArrayImage',
    }),
    defineField({
      name: 'button',
      title: 'Call to Action Button',
      type: 'button',
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'description.0.value',
      media: 'image.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled CTA Section',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})