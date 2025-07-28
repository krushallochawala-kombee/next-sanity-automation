import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'header',
  title: 'Header',
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
      name: 'mainNavigation',
      title: 'Main Navigation',
      type: 'array',
      of: [{type: 'link'}],
      description: 'Links in the main navigation bar.',
      validation: (Rule) => Rule.required().min(1),
    }),
    defineField({
      name: 'ctaButton',
      title: 'Call-to-Action Button',
      type: 'button',
      description: 'An optional call-to-action button in the header.',
    }),
  ],
  preview: {
    select: {
      logoMedia: 'logo.image.asset', // Assuming 'companylogo' document has an 'image' field of type image
      navItemCount: 'mainNavigation.length',
    },
    prepare({logoMedia, navItemCount}) {
      return {
        title: 'Global Header',
        subtitle: navItemCount ? `${navItemCount} Navigation Items` : 'No Navigation Items',
        media: logoMedia,
      }
    },
  },
})