import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'textblock',
  title: 'Text Block',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Title',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'content',
      title: 'Content',
      type: 'internationalizedArrayText',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      content: 'content.0.value',
    },
    prepare({title, content}) {
      const truncatedContent = content ? `${content.substring(0, 50)}...` : 'No content';
      return {
        title: title || 'Untitled Text Block',
        subtitle: truncatedContent,
      }
    },
  },
})