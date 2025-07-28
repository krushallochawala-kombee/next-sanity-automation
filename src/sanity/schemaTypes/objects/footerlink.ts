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
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'link',
      title: 'Link Destination',
      type: 'link', // Reference to the 'link' object type
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      url: 'link.url.0.value', // Assuming the 'link' object has an internationalized 'url' field
      pageTitle: 'link.internalLink->title.0.value', // Assuming 'link' can reference a page
    },
    prepare({title, url, pageTitle}) {
      const subtitle = url || pageTitle || 'No destination set';
      return {
        title: title || 'Untitled Footer Link',
        subtitle: subtitle,
      }
    },
  },
})