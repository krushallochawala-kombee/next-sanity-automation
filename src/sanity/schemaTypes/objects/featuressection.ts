import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'featuressection',
  title: 'Features Section',
  type: 'object',
  fields: [
    defineField({
      name: 'name',
      title: 'Section Name (internal)',
      type: 'string',
      description: 'Used for internal identification in the Studio. Not displayed on the website.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'title',
      title: 'Section Title',
      type: 'internationalizedArrayString',
      description: 'The main heading for the features section.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Section Description',
      type: 'internationalizedArrayText',
      description: 'A brief description or subtitle for the features section.',
    }),
    defineField({
      name: 'features',
      title: 'Features',
      type: 'array',
      of: [{type: 'reference', to: [{type: 'feature'}]}],
      description: 'Select the individual features to display in this section.',
      validation: (Rule) => Rule.min(1).required(),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      description: 'description.0.value',
      featureCount: 'features.length',
    },
    prepare({title, description, featureCount}) {
      const featureText = featureCount === 1 ? '1 Feature' : `${featureCount || 0} Features`;
      return {
        title: title || 'Untitled Features Section',
        subtitle: description ? `${description} (${featureText})` : `(${featureText})`,
      }
    },
  },
})
