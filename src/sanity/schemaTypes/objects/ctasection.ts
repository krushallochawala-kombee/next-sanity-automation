import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'ctasection',
  title: 'Call to Action Section',
  type: 'object',
  fields: [
    defineField({
      name: 'headline',
      title: 'Headline',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'callToAction',
      title: 'Call to Action Button',
      type: 'button',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'headline.0.value',
      subtitle: 'description.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled CTA Section',
        subtitle: subtitle || 'No description',
      }
    },
  },
})