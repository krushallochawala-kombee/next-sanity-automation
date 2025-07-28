import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metricssection',
  title: 'Metrics Section',
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
      name: 'metrics',
      title: 'Metrics',
      type: 'array',
      of: [{type: 'metric'}],
      validation: (Rule) => Rule.min(1),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'description.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled Metrics Section',
        subtitle: subtitle,
      }
    },
  },
})