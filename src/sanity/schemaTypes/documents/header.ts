import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'header',
  title: 'Global Header',
  type: 'document',
  fields: [
    defineField({
      name: 'logo',
      title: 'Company Logo',
      type: 'reference',
      to: [{type: 'companylogo'}],
      description: 'The logo displayed in the header.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'navigationLinks',
      title: 'Navigation Links',
      type: 'array',
      of: [
        {
          type: 'reference',
          to: [{type: 'page'}],
        },
      ],
      description: 'Links that appear in the main navigation menu.',
      validation: (Rule) => Rule.min(1).error('At least one navigation link is required.'),
    }),
    defineField({
      name: 'callToActionButton',
      title: 'Call to Action Button',
      type: 'reference',
      to: [{type: 'button'}],
      description: 'Optional call to action button in the header.',
    }),
  ],
  preview: {
    select: {
      navCount: 'navigationLinks.length',
    },
    prepare({navCount}) {
      return {
        title: 'Global Header Settings',
        subtitle: `Navigation Links: ${navCount || 0}`,
      }
    },
  },
})
