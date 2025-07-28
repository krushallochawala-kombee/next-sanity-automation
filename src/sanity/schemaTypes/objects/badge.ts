import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'badge',
  title: 'Badge',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'icon',
      title: 'Icon',
      type: 'internationalizedArrayImage',
      description: 'Optional icon for the badge',
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      media: 'icon.0.value.asset',
    },
    prepare({title, media}) {
      return {
        title: title || 'Untitled Badge',
        media: media,
      }
    },
  },
})