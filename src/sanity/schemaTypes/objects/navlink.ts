import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'navlink',
  title: 'Navigation Link',
  type: 'object',
  fields: [
    defineField({
      name: 'label',
      title: 'Label',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'External URL',
      type: 'internationalizedArrayUrl',
      description: 'Optional: Use for external links. If both URL and Reference are provided, URL will take precedence.',
    }),
    defineField({
      name: 'reference',
      title: 'Internal Page',
      type: 'reference',
      to: [{type: 'page'}],
      description: 'Optional: Link to an internal page.',
    }),
  ],
  preview: {
    select: {
      label: 'label',
      url: 'url',
      reference: 'reference',
    },
    prepare({label, url, reference}) {
      const displayLabel = label?.[0]?.value || 'Untitled Nav Link';
      let displaySubtitle = '';

      if (url?.[0]?.value) {
        displaySubtitle = `URL: ${url[0].value}`;
      } else if (reference?._ref) {
        displaySubtitle = `Internal Link (ID: ${reference._ref})`;
      } else {
        displaySubtitle = 'No destination set';
      }

      return {
        title: displayLabel,
        subtitle: displaySubtitle,
      }
    },
  },
})