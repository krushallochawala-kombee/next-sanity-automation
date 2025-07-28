import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'ctasection',
  title: 'CTA Section',
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
      name: 'callToActionButton',
      title: 'Call to Action Button',
      type: 'button',
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'description.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled CTA Section',
        subtitle: subtitle,
      }
    },
  },
})