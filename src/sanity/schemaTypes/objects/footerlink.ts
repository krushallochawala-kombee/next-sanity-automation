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
      name: 'destination',
      title: 'Destination',
      description: 'Select an internal page or provide an external URL.',
      type: 'array',
      validation: (Rule) => Rule.required().max(1), // Ensures only one destination is selected
      of: [
        {
          type: 'object',
          name: 'externalUrl',
          title: 'External URL',
          fields: [
            defineField({
              name: 'url',
              title: 'URL',
              type: 'internationalizedArrayUrl', // Rule 6: Use internationalizedArrayUrl for URL fields
              validation: (Rule) => Rule.required(),
            }),
          ],
          preview: {
            select: {
              url: 'url.0.value', // For internationalizedArrayUrl
            },
            prepare({url}) {
              return {
                title: url || 'External URL (Not Set)',
                subtitle: 'External Link',
              }
            },
          },
        },
        {
          type: 'reference',
          name: 'internalPage',
          title: 'Internal Page',
          to: [{type: 'page'}], // Rule 5 & 3b: Reference to 'page' document
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value', // Rule 7: For i18n string fields
      internalPageTitle: 'destination[0].internalPage->title.0.value', // Get title from referenced page
      externalUrl: 'destination[0].externalUrl.url.0.value', // Get URL from external URL object
    },
    prepare({title, internalPageTitle, externalUrl}) {
      let subtitle = 'No Destination';
      if (internalPageTitle) {
        subtitle = `Internal: ${internalPageTitle}`;
      } else if (externalUrl) {
        subtitle = `External: ${externalUrl}`;
      }
      return {
        title: title || 'Untitled Footer Link',
        subtitle: subtitle,
      }
    },
  },
})
