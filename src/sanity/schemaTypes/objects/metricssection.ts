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
          to: [{type: 'metricitem'}],
        },
      ],
      validation: (Rule) => Rule.required().min(1),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      subtitle: 'description.0.value',
      metricCount: 'metrics.length',
    },
    prepare({title, subtitle, metricCount}) {
      const metricsText = metricCount === 1 ? '1 Metric' : `${metricCount || 0} Metrics`;
      return {
        title: title || 'Untitled Metrics Section',
        subtitle: subtitle ? `${subtitle} (${metricsText})` : metricsText,
      }
    },
  },
})