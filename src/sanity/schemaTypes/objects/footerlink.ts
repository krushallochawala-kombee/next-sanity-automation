import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'footerlink',
  title: 'Footer Link',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Link Label',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'link',
      title: 'Link Target',
      type: 'array',
      validation: (Rule) => Rule.length(1).required(),
      of: [
        {
          type: 'object',
          name: 'externalLink',
          title: 'External URL',
          fields: [
            defineField({
              name: 'url',
              title: 'URL',
              type: 'internationalizedArrayUrl',
              validation: (Rule) => Rule.required(),
            }),
          ],
          preview: {
            select: {
              url: 'url.0.value',
            },
            prepare({url}) {
              return {
                title: url || 'Untitled External Link',
                subtitle: 'External Link',
              }
            },
          },
        },
        {
          type: 'reference',
          name: 'internalLink',
          title: 'Internal Page',
          to: [{type: 'page'}],
          options: {
            disableNew: true, // Typically, you wouldn't create new pages from a link field
          },
          preview: {
            select: {
              title: 'title.0.value', // Assuming 'page' has an i18n title
              subtitle: 'slug.current', // Assuming 'page' has a slug
            },
            prepare({title, subtitle}) {
              return {
                title: title || 'Untitled Internal Page',
                subtitle: `Internal Page: ${subtitle || 'No Slug'}`,
              }
            },
          },
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      linkType: 'link.0._type',
      externalUrl: 'link.0.url.0.value',
      internalPageRef: 'link.0.title.0.value', // Assuming referenced 'page' has a title
    },
    prepare({title, linkType, externalUrl, internalPageRef}) {
      let subtitle = 'No Link Target';
      if (linkType === 'externalLink' && externalUrl) {
        subtitle = `External: ${externalUrl}`;
      } else if (linkType === 'internalLink' && internalPageRef) {
        subtitle = `Internal: ${internalPageRef}`;
      } else if (linkType === 'internalLink') {
        subtitle = 'Internal Page (No Title)';
      }

      return {
        title: title || 'Untitled Footer Link',
        subtitle: subtitle,
      }
    },
  },
})