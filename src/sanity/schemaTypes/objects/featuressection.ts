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
      of: [{type: 'reference', to: [{type: 'featureitem'}]}],
      validation: (Rule) => Rule.min(1).error('A features section must have at least one feature.'),
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
        subtitle: subtitle || 'No description provided',
      }
    },
  },
})