import { defineType, defineField } from "sanity";

export default defineType({
  name: "page",
  title: "Page",
  type: "document",
  fields: [
    defineField({
      name: "title",
      title: "Title",
      type: "internationalizedArrayString",
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "slug",
      title: "Slug",
      type: "internationalizedArraySlug",
      options: {
        source: "title.0.value", // Assuming first language title is the source
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: "pageBuilder",
      title: "Page Builder",
      type: "array",
      of: [
        { type: "herosection" },
        { type: "ctasection" },
        { type: "featuressection" },
        { type: "metricssection" },
        { type: "quotesection" },
        { type: "socialproofsection" },
        // Note: 'badge', 'button', 'footerlink', 'footerlinkcolumn', 'logo', 'navigationlink'
        // are typically embedded within other sections or used as standalone objects,
        // not usually top-level page builder components.
        // Including only common section types here as per "Minimal Field Approach".
        // If they *must* be page builder components as per instructions, they'd be added:
        // {type: 'badge'},
        // {type: 'button'},
        // {type: 'footerlink'},
        // {type: 'footerlinkcolumn'},
        // {type: 'logo'},
        // {type: 'navigationlink'},
      ],
    }),
  ],
  preview: {
    select: {
      title: "title.0.value",
      slug: "slug.0.current",
    },
    prepare({ title, slug }) {
      return {
        title: title || "Untitled Page",
        subtitle: slug ? `/${slug}` : "No slug",
      };
    },
  },
});
