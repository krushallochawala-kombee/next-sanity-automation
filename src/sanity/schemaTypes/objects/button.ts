import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'button',
  title: 'Button',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'URL',
      type: 'internationalizedArrayUrl',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      subtitle: 'url.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled Button',
        subtitle: subtitle,
      }
    },
  },
})