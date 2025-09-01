import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'socialproofsection',
  title: 'Social Proof Section',
  type: 'object',
  fields: [
    defineField({
      name: 'title',
      title: 'Section Title',
      type: 'internationalizedArrayString',
      description: 'Optional title for the social proof section.',
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
      description: 'Optional descriptive text for the section.',
    }),
    defineField({
      name: 'companyLogos',
      title: 'Company Logos',
      type: 'array',
      of: [{type: 'reference', to: [{type: 'companylogo'}]}],
      description: 'Add logos of companies or clients for social proof.',
    }),
    defineField({
      name: 'testimonials',
      title: 'Testimonials',
      type: 'array',
      of: [
        {
          type: 'object',
          name: 'testimonialItem',
          title: 'Testimonial',
          fields: [
            defineField({
              name: 'quote',
              title: 'Quote',
              type: 'internationalizedArrayText',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'authorName',
              title: 'Author Name',
              type: 'internationalizedArrayString',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'authorTitle',
              title: 'Author Title',
              type: 'internationalizedArrayString',
              description: 'e.g., "CEO of Company X"',
            }),
            defineField({
              name: 'authorImage',
              title: 'Author Image',
              type: 'internationalizedArrayImage',
            }),
          ],
          preview: {
            select: {
              title: 'authorName.0.value',
              subtitle: 'quote.0.value',
              media: 'authorImage.0.value.asset',
            },
            prepare({title, subtitle, media}) {
              return {
                title: title || 'Untitled Testimonial',
                subtitle: subtitle,
                media: media,
              }
            },
          },
        },
      ],
      description: 'Add customer testimonials to this section.',
    }),
  ],
  preview: {
    select: {
      title: 'title.0.value',
      description: 'description.0.value',
      firstLogoImage: 'companyLogos.0->logo.0.value.asset', // Assuming companylogo document has a 'logo' field of type internationalizedArrayImage
      testimonialCount: 'testimonials.length',
    },
    prepare({title, description, firstLogoImage, testimonialCount}) {
      const subtitleParts = [];
      if (description) {
        subtitleParts.push(description);
      }
      if (testimonialCount > 0) {
        subtitleParts.push(`${testimonialCount} Testimonial${testimonialCount === 1 ? '' : 's'}`);
      }
      const subtitle = subtitleParts.join(' | ');

      return {
        title: title || 'Social Proof Section',
        subtitle: subtitle,
        media: firstLogoImage,
      }
    },
  },
})