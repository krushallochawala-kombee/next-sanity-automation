import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metric',
  title: 'Metric',
  type: 'document',
  fields: [
    defineField({
      name: 'value',
      title: 'Value',
      type: 'internationalizedArrayString',
      description: 'The numeric or text value of the metric (e.g., "10K+", "99%") ',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      description: 'A brief label describing the metric (e.g., "Happy Customers", "Projects Completed")',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      description: 'Optional, longer description for the metric.',
    }),
  ],
  preview: {
    select: {
      value: 'value.0.value',
      label: 'label.0.value',
    },
    prepare({value, label}) {
      return {
        title: value || 'Untitled Metric',
        subtitle: label,
      }
    },
  },
})