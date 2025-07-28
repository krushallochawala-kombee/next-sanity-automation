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
      title: 'Description',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'metrics',
      title: 'Metrics',
      type: 'array',
      of: [{type: 'metricitem'}],
      validation: (Rule) => Rule.required().min(1),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      description: 'description.0.value',
      metricCount: 'metrics.length',
    },
    prepare({title, description, metricCount}) {
      const subtitle = metricCount
        ? `${metricCount} metric${metricCount === 1 ? '' : 's'}`
        : description || 'No metrics defined';

      return {
        title: title || 'Metrics Section',
        subtitle: subtitle,
        media: undefined, // Metrics section typically doesn't have a main image
      }
    },
  },
})