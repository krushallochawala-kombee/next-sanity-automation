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
      of: [
        {
          type: 'reference',
          to: [{type: 'metric'}],
          name: 'metric', // Unique name for this item type in the array
        },
      ],
      validation: (Rule) => Rule.min(1).max(4), // Typically 3-4 metrics in a section
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