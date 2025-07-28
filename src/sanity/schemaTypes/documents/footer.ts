import { defineType, defineField } from "sanity";

export default defineType({
  name: "footer",
  title: "Footer",
  type: "document",
  fields: [
    defineField({
      name: "columns",
      title: "Link Columns",
      description: "The columns of links displayed in the footer.",
      type: "array",
      of: [
        {
          type: "reference",
          to: [{ type: "footerlinkscolumn" }],
          // Rule 3d: When an array contains multiple items of the same type, each must have a unique name.
          // In this case, each item is a reference, and Sanity automatically assigns unique _key values.
          // No explicit 'name' property is needed here for references.
        },
      ],
      validation: (Rule) => Rule.required().min(1),
    }),
    defineField({
      name: "companyLogo",
      title: "Company Logo",
      description: "The logo displayed in the footer.",
      type: "reference",
      to: [{ type: "companylogo" }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "copyright",
      title: "Copyright Text",
      description: "The copyright text displayed at the bottom of the footer.",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: "title", // Singleton, so name is enough
    },
    prepare({ title }) {
      return {
        title: title || "Footer Settings",
        subtitle: "Global Footer Content (Singleton)",
      };
    },
  },
});
