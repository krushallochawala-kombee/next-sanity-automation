import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metricssection',
  title: 'Metrics Section',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Section Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Section Description',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'metrics',
      title: 'Metrics',
      type: 'array',
      validation: (Rule) => Rule.required().min(1),
      of: [
        {
          type: 'metricitem',
        },
      ],
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