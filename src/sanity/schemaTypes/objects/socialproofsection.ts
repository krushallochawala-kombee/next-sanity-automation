import {defineType, defineField} from 'sanity'

export default defineType({
  name: 'socialproofsection',
  title: 'Social Proof Section',
  type: 'object',
  fields: [
    defineField({
      name: 'heading',
      title: 'Heading',
      type: 'internationalizedArrayString',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'internationalizedArrayText',
    }),
    defineField({
      name: 'testimonials',
      title: 'Testimonials',
      type: 'array',
      validation: (Rule) => Rule.required().min(1),
      of: [
        {
          name: 'testimonialItem',
          type: 'object',
          title: 'Testimonial',
          fields: [
            defineField({
              name: 'quote',
              title: 'Quote',
              type: 'internationalizedArrayText',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'author',
              title: 'Author',
              type: 'internationalizedArrayString',
              validation: (Rule) => Rule.required(),
            }),
            defineField({
              name: 'role',
              title: 'Role/Company',
              type: 'internationalizedArrayString',
            }),
            defineField({
              name: 'image',
              title: 'Author Image',
              type: 'internationalizedArrayImage',
            }),
          ],
          preview: {
            select: {
              title: 'author.0.value',
              subtitle: 'quote.0.value',
              media: 'image.0.value.asset',
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
    }),
  ],
  preview: {
    select: {
      title: 'heading.0.value',
      subtitle: 'description.0.value',
    },
    prepare({title, subtitle}) {
      return {
        title: title || 'Social Proof Section',
        subtitle: subtitle || 'Displays client testimonials',
      }
    },
  },
})
