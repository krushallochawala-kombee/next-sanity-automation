import { defineType, defineField } from "sanity";

export default defineType({
  name: "logo",
  title: "Logo",
  type: "object",
  fields: [
    defineField({
      name: "image",
      title: "Image",
      type: "internationalizedArrayImage",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "altText",
      title: "Alternative Text",
      description:
        "Important for accessibility and SEO. Describes the image content.",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "url",
      title: "URL",
      description: "Optional. The URL the logo links to.",
      type: "internationalizedArrayUrl",
    }),
  ],
  preview: {
    select: {
      title: "altText.0.value",
      media: "image.0.value.asset",
    },
    prepare({ title, media }) {
      return {
        title: title || "Untitled Logo",
        media: media,
      };
    },
  },
});
