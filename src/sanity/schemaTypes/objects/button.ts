import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'button',
  title: 'Button',
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
      title: 'Link',
      description: 'Choose either an internal page or an external URL.',
      type: 'object',
      fields: [
        defineField({
          name: 'internalLink',
          title: 'Internal Link',
          type: 'reference',
          to: [{type: 'page'}], // Referencing available 'page' document
          hidden: ({parent}) => !!parent?.externalLink, // Hide if external link is set
        }),
        defineField({
          name: 'externalLink',
          title: 'External URL',
          type: 'internationalizedArrayUrl',
          hidden: ({parent}) => !!parent?.internalLink, // Hide if internal link is set
        }),
      ],
      validation: (Rule) =>
        Rule.custom((fields) => {
          if (!fields?.internalLink && !fields?.externalLink) {
            return 'A button must have either an internal link or an external URL.'
          }
          if (fields?.internalLink && fields?.externalLink) {
            return 'A button cannot have both an internal link and an external URL.'
          }
          return true
        }),
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      internalLinkSlug: 'link.internalLink->slug.current',
      externalLinkUrl: 'link.externalLink.0.value',
    },
    prepare({title, internalLinkSlug, externalLinkUrl}) {
      let subtitle = 'No link set';
      if (internalLinkSlug) {
        subtitle = `Internal: /${internalLinkSlug}`;
      } else if (externalLinkUrl) {
        subtitle = `External: ${externalLinkUrl}`;
      }
      return {
        title: title || 'Untitled Button',
        subtitle: subtitle,
      };
    },
  },
})
