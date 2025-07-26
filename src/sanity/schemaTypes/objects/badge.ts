import { defineType, defineField } from "sanity";

export default defineType({
  name: "badge",
  title: "Badge",
  type: "object",
  fields: [
    defineField({
      name: "label",
      title: "Label",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: "label.0.value",
    },
    prepare({ title }) {
      return {
        title: title || "Untitled Badge",
      };
    },
  },
});
