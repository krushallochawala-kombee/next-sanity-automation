import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'siteSettings',
  title: 'Site Settings',
  type: 'document',
  fields: [
    defineField({
      name: 'siteName',
      title: 'Site Name',
      type: 'internationalizedArrayString',
      description: 'The global name of your website. Used in titles and branding.',
    }),
    defineField({
      name: 'siteDescription',
      title: 'Site Description',
      type: 'internationalizedArrayText',
      description: 'A brief description of your site, used for SEO and meta tags.',
    }),
    defineField({
      name: 'header',
      title: 'Global Header',
      type: 'reference',
      to: [{type: 'header'}],
      description: 'Select the global header for your site.',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'footer',
      title: 'Global Footer',
      type: 'reference',
      to: [{type: 'footer'}],
      description: 'Select the global footer for your site.',
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      siteName: 'siteName.0.value',
      siteDescription: 'siteDescription.0.value',
    },
    prepare({siteName, siteDescription}) {
      return {
        title: 'Site Settings',
        subtitle: siteName || siteDescription || 'Global settings for the website',
      }
    },
  },
})