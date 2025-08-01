import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metricitem',
  title: 'Metric Item',
  type: 'object',
  fields: [
    defineField({
      name: 'value',
      title: 'Value',
      type: 'internationalizedArrayString',
      description: 'The numeric or text value for the metric (e.g., "10k+", "99%")'
    }),
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      description: 'A descriptive label for the metric (e.g., "Happy Customers")'
    }),
  ],
  preview: {
    select: {
      title: 'value.0.value',
      subtitle: 'label.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Untitled Metric',
        subtitle: subtitle,
      }
    },
  },
})