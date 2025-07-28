import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'link',
  title: 'Link',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'externalUrl',
      title: 'External URL',
      type: 'internationalizedArrayUrl',
      description: 'The URL for an external website.',
      validation: (Rule) =>
        Rule.custom((currentValue, context) => {
          const {internalLink} = context.parent as {internalLink?: {_ref?: string}}
          if (!currentValue && !internalLink) {
            return 'Either an External URL or an Internal Page must be provided.'
          }
          if (currentValue && internalLink) {
            return 'Cannot have both an External URL and an Internal Page. Please choose one.'
          }
          return true
        }),
    }),
    defineField({
      name: 'internalLink',
      title: 'Internal Page',
      type: 'reference',
      to: [{type: 'page'}],
      description: 'Reference to an internal page within the site.',
      validation: (Rule) =>
        Rule.custom((currentValue, context) => {
          const {externalUrl} = context.parent as {externalUrl?: {0?: {value?: string}}}
          if (!currentValue && !externalUrl) {
            return 'Either an External URL or an Internal Page must be provided.'
          }
          if (currentValue && externalUrl) {
            return 'Cannot have both an External URL and an Internal Page. Please choose one.'
          }
          return true
        }),
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      externalUrl: 'externalUrl.0.value',
      pageTitle: 'internalLink->title.0.value', // Select title from referenced 'page'
    },
    prepare({title, externalUrl, pageTitle}) {
      const subtitle = externalUrl
        ? `External: ${externalUrl}`
        : pageTitle
        ? `Internal: ${pageTitle}`
        : 'No target set';

      return {
        title: title || 'Untitled Link',
        subtitle: subtitle,
      }
    },
  },
})
