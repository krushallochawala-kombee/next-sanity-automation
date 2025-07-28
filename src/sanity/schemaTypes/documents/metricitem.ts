import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metricitem',
  title: 'Metric Item',
  type: 'document',
  fields: [
    defineField({
      name: 'value',
      title: 'Metric Value/Number',
      type: 'internationalizedArrayString',
      description: 'The numeric value or primary text of the metric (e.g., "10M+", "99%").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'label',
      title: 'Metric Label/Description',
      type: 'internationalizedArrayText',
      description: 'A short description or label for the metric (e.g., "Active Users", "Customer Satisfaction").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'icon',
      title: 'Icon',
      type: 'internationalizedArrayImage',
      description: 'An optional icon to visually represent the metric.',
    }),
  ],
  preview: {
    select: {
      value: 'value.0.value',
      label: 'label.0.value',
      media: 'icon.0.value.asset',
    },
    prepare({value, label, media}) {
      const title = value ? `${value} ${label || ''}`.trim() : 'Untitled Metric';
      const subtitle = label && value ? label : (value ? 'No label provided' : 'No value provided');
      return {
        title: title,
        subtitle: subtitle,
        media: media,
      }
    },
  },
})