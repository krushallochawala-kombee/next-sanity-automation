import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'header',
  title: 'Header',
  type: 'document',
  fields: [
    defineField({
      name: 'logo',
      title: 'Site Logo',
      type: 'imagewithalt', // Reference to the 'imagewithalt' object type
      description: 'The main logo displayed in the header.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'mainNavigation',
      title: 'Main Navigation',
      type: 'array',
      description: 'Links for the primary navigation menu.',
      of: [
        {type: 'link'} // Reference to the 'link' object type
      ],
      validation: (Rule) => Rule.min(1).max(5), // Keep navigation concise
    }),
    defineField({
      name: 'ctaButton',
      title: 'Call-to-Action Button',
      type: 'button', // Reference to the 'button' object type
      description: 'Optional call-to-action button in the header.',
    }),
  ],
  preview: {
    select: {
      logoImage: 'logo.image.asset', // Assuming imagewithalt has an 'image' field of type 'image'
      logoAlt: 'logo.alt.0.value', // Assuming imagewithalt has an 'alt' field of type 'internationalizedArrayString'
      navItems: 'mainNavigation', // Select the array to get its length
    },
    prepare({logoImage, logoAlt, navItems}) {
      const navCount = navItems ? navItems.length : 0;
      return {
        title: 'Global Header',
        subtitle: `Logo: ${logoAlt || 'Untitled'} | ${navCount} Navigation Items`,
        media: logoImage,
      }
    },
  },
})
