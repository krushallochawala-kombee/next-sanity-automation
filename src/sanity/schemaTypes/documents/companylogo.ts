import { defineType, defineField } from "sanity";

export default defineType({
  name: "companylogo",
  title: "Company Logo",
  type: "document",
  fields: [
    defineField({
      name: "name",
      title: "Company Name",
      type: "internationalizedArrayString",
      description: "The name of the company for this logo.",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "logoImage",
      title: "Logo Image",
      type: "internationalizedArrayImage",
      description: "The company logo image.",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "linkUrl",
      title: "Link URL",
      type: "internationalizedArrayUrl",
      description: "Optional URL the logo links to (e.g., company website).",
    }),
  ],
  preview: {
    select: {
      title: "name.0.value",
      media: "logoImage.0.value.asset",
    },
    prepare({ title, media }) {
      return {
        title: title || "Untitled Logo",
        media: media,
      };
    },
  },
});
