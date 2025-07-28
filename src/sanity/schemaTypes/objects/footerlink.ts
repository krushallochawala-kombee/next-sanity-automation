import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footerlink',
  title: 'Footer Link',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      description: 'The visible text for the footer link.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'link',
      title: 'Link Target',
      type: 'reference',
      to: [{type: 'page'}],
      description: 'The internal page this footer link points to.',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      linkTitle: 'link->title.0.value',
    },
    prepare({title, linkTitle}) {
      return {
        title: title || 'Untitled Footer Link',
        subtitle: linkTitle ? `Points to: ${linkTitle}` : 'No page linked',
      }
    },
  },
})