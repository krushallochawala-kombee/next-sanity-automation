import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'featuressection',
  title: 'Features Section',
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
      name: 'features',
      title: 'Features',
      type: 'array',
      validation: (Rule) => Rule.required().min(1),
      of: [
        {
          type: 'reference',
          to: [{type: 'feature'}],
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
        title: title || 'Untitled Features Section',
        subtitle: subtitle,
      }
    },
  },
})