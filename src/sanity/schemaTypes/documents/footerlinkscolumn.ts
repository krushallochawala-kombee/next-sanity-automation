import { defineType, defineField } from "sanity";

export default defineType({
  name: "footerlinkscolumn",
  title: "Footer Links Column",
  type: "document",
  fields: [
    defineField({
      name: "title",
      title: "Column Title",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "links",
      title: "Links",
      type: "array",
      of: [{ type: "footerlink" }],
      validation: (Rule) => Rule.required().min(1),
    }),
  ],
  preview: {
    select: {
      title: "title.0.value",
    },
    prepare({ title }) {
      return {
        title: title || "Untitled Footer Links Column",
      };
    },
  },
});
