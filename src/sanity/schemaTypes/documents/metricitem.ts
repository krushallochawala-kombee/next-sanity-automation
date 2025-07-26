import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'metricitem',
  title: 'Metric Item',
  type: 'document',
  fields: [
    defineField({
      name: 'value',
      title: 'Value',
      type: 'internationalizedArrayString',
      description: 'The numeric value or short text for the metric (e.g., "10M+", "99%").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      description: 'A brief description or label for the metric.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'icon',
      title: 'Icon',
      type: 'internationalizedArrayImage',
      description: 'An optional icon associated with the metric.',
    }),
  ],
  preview: {
    select: {
      title: 'value.0.value',
      subtitle: 'description.0.value',
      media: 'icon.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Metric',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})