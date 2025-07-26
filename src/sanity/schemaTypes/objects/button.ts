import { defineType, defineField } from "sanity";

export default defineType({
  name: "button",
  type: "object",
  title: "Button",
  fields: [
    defineField({
      name: "label",
      type: "internationalizedArrayString",
      title: "Label",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "linkTarget",
      type: "array",
      title: "Link Target",
      description: "Choose either an external URL or an internal page link.",
      of: [
        {
          type: "object",
          name: "externalLink",
          title: "External URL",
          fields: [
            defineField({
              name: "url",
              type: "internationalizedArrayUrl",
              title: "URL",
              validation: (Rule) => Rule.required(),
            }),
          ],
          preview: {
            select: {
              title: "url.0.value",
            },
            prepare({ title }) {
              return {
                title: `External: ${title || "No URL provided"}`,
              };
            },
          },
        },
        {
          type: "reference",
          name: "internalLink",
          title: "Internal Link",
          to: [{ type: "page" }],
          validation: (Rule) => Rule.required(),
        },
      ],
      validation: (Rule) =>
        Rule.max(1)
          .error("Please select only one link type (external or internal).")
          .min(1)
          .error("A link target is required for the button."),
    }),
  ],
  preview: {
    select: {
      title: "label.0.value",
      linkType: "linkTarget.0._type",
    },
    prepare({ title, linkType }) {
      let subtitle = "";
      if (linkType === "externalLink") {
        subtitle = "External Link";
      } else if (linkType === "internalLink") {
        subtitle = "Internal Link";
      }
      return {
        title: title || "Untitled Button",
        subtitle: subtitle,
      };
    },
  },
});
