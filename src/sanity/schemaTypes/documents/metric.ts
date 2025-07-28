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
      description: 'The numeric or text value of the metric (e.g., "10k+", "99%").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayText',
      description: 'A short description or label for the metric (e.g., "Happy Customers").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'icon',
      title: 'Icon',
      type: 'internationalizedArrayImage',
      description: 'An optional icon representing the metric.',
    }),
  ],
  preview: {
    select: {
      title: 'value.0.value',
      subtitle: 'label.0.value',
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
