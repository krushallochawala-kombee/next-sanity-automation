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
      description: 'The text displayed on the button.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'url',
      title: 'External URL',
      type: 'internationalizedArrayUrl',
      description: 'The external URL the button links to (e.g., https://example.com).',
    }),
    defineField({
      name: 'reference',
      title: 'Internal Page Reference',
      type: 'reference',
      to: [{type: 'page'}],
      description: 'Link to an internal page within Sanity.',
    }),
  ],
  preview: {
    select: {
      title: 'label.0.value',
      urlArray: 'url',
      reference: 'reference',
    },
    prepare({title, urlArray, reference}) {
      let subtitle = '';
      if (urlArray && urlArray.length > 0 && urlArray[0].value) {
        subtitle = `External: ${urlArray[0].value}`;
      } else if (reference) {
        subtitle = 'Internal Page Reference';
      } else {
        subtitle = 'No destination set';
      }
      return {
        title: title || 'Untitled Button',
        subtitle: subtitle,
      }
    },
  },
})