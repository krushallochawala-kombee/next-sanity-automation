import { defineType, defineField } from "sanity";

export default defineType({
  name: "siteSettings",
  title: "Site Settings",
  type: "document",
  fields: [
    defineField({
      name: "name",
      title: "Settings Name",
      type: "internationalizedArrayString",
      description: 'A name for these settings (e.g., "Main Site Settings").',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "header",
      title: "Header",
      type: "reference",
      to: [{ type: "header" }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "footer",
      title: "Footer",
      type: "reference",
      to: [{ type: "footer" }],
      validation: (Rule) => Rule.required(),
    }),
  ],
});
