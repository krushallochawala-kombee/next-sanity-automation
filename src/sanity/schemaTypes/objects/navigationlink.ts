import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'navigationlink',
  title: 'Navigation Link',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      description: 'The display text for the navigation link.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'link',
      title: 'Link Destination',
      type: 'object',
      description: 'Select an internal page or provide an external URL for the link.',
      validation: (Rule) =>
        Rule.required().custom((value, context) => {
          if (!value) {
            return 'Link destination is required.';
          }
          const { pageReference, externalUrl } = value;

          const hasPageRef = !!pageReference?._ref;
          const hasExternalUrl = Array.isArray(externalUrl) && externalUrl.some(item => !!item.value);

          if (hasPageRef && hasExternalUrl) {
            return 'Please select either an internal page or provide an external URL, not both.';
          }
          if (!hasPageRef && !hasExternalUrl) {
            return 'Please select an internal page or provide an external URL.';
          }
          return true;
        }),
      fields: [
        defineField({
          name: 'pageReference',
          title: 'Internal Page',
          type: 'reference',
          to: [{type: 'page'}],
          description: 'Link to an internal page within the site.',
        }),
        defineField({
          name: 'externalUrl',
          title: 'External URL',
          type: 'internationalizedArrayUrl',
          description: 'Link to an external website or a relative path (e.g., /about-us).',
        }),
      ],
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      pageRefTitle: 'link.pageReference->title',
      externalUrl: 'link.externalUrl.0.value',
    },
    prepare({title, pageRefTitle, externalUrl}) {
      const subtitle = pageRefTitle 
        ? `Internal: ${pageRefTitle}` 
        : (externalUrl ? `External: ${externalUrl}` : 'No link set');
      return {
        title: title || 'Untitled Link',
        subtitle: subtitle,
      };
    },
  },
})