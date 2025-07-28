import { defineType, defineField } from "sanity";

export default defineType({
  name: "header",
  title: "Header",
  type: "document",
  fields: [
    defineField({
      name: "logo",
      title: "Company Logo",
      type: "reference",
      to: [{ type: "companylogo" }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "navigationLinks",
      title: "Navigation Links",
      type: "array",
      of: [{ type: "navlink" }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "ctaButton",
      title: "Call to Action Button",
      type: "button",
    }),
  ],
  preview: {
    select: {
      logoImage: "logo.image.asset",
    },
    prepare({ logoImage }) {
      return {
        title: "Header Settings",
        subtitle: "Manage site-wide header content",
        media: logoImage,
      };
    },
  },
});
