import { defineType, defineField } from "sanity";

export default defineType({
  name: "feature",
  title: "Feature",
  type: "document",
  fields: [
    defineField({
      name: "title",
      title: "Title",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "description",
      title: "Description",
      type: "internationalizedArrayText",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "image",
      title: "Image",
      type: "internationalizedArrayImage",
      options: {
        hotspot: true,
      },
    }),
  ],
  preview: {
    select: {
      title: "title.0.value",
      subtitle: "description.0.value",
      media: "image.0.value.asset",
    },
    prepare({ title, subtitle, media }) {
      return {
        title: title || "Untitled Feature",
        subtitle: subtitle,
        media: media,
      };
    },
  },
});
