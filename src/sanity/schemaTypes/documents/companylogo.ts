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
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "logo",
      title: "Logo Image",
      type: "internationalizedArrayImage",
      description: "Upload the company logo image.",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "url",
      title: "Company Website URL",
      type: "internationalizedArrayUrl",
      description: "Optional: URL the logo should link to.",
    }),
  ],

  preview: {
    select: {
      title: "name.0.value",
      media: "logo.0.value.asset",
    },
    prepare({ title, media }) {
      return {
        title: title || "Untitled Company Logo",
        media: media,
      };
    },
  },
});
