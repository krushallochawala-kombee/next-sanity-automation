import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metricitem',
  title: 'Metric Item',
  type: 'document',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      description: 'The descriptive label for the metric (e.g., "Happy Customers").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'value',
      title: 'Value',
      type: 'internationalizedArrayString',
      description: 'The metric value (e.g., "10K+", "99%").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      description: 'An optional, longer description for the metric.',
    }),
    defineField({
      name: 'icon',
      title: 'Icon',
      type: 'internationalizedArrayImage',
      description: 'An optional icon to represent the metric.',
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      subtitle: 'value.0.value',
      media: 'icon.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Metric',
        subtitle: subtitle ? `Value: ${subtitle}` : '',
        media: media,
      }
    },
  },
})