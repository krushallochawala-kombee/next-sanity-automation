import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'persondetails',
  title: 'Person Details',
  type: 'object',
  fields: [
    defineField({
      name: 'name',
      title: 'Name',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'role',
      title: 'Role',
      type: 'internationalizedArrayString',
    }),
    defineField({
      name: 'image',
      title: 'Image',
      type: 'internationalizedArrayImage',
    }),
  ],
  preview: {
    select: {
      title: 'name.0.value',
      subtitle: 'role.0.value',
      media: 'image.0.value.asset',
    },
    prepare({title, subtitle, media}) {
      return {
        title: title || 'Untitled Person',
        subtitle: subtitle,
        media: media,
      }
    },
  },
})