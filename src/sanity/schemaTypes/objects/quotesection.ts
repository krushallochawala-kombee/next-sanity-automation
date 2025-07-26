import { defineType, defineField } from "sanity";

export default defineType({
  name: "quotesection",
  title: "Quote Section",
  type: "object",
  fields: [
    defineField({
      name: "quote",
      title: "Quote",
      type: "internationalizedArrayText",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "author",
      title: "Author",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "source",
      title: "Source / Role",
      type: "internationalizedArrayString",
    }),
  ],
  preview: {
    select: {
      title: "quote.0.value",
      subtitle: "author.0.value",
    },
    prepare({ title, subtitle }) {
      return {
        title: title || "Untitled Quote Section",
        subtitle: subtitle ? `by ${subtitle}` : "",
      };
    },
  },
});
