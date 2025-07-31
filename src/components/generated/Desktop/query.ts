import { groq } from "next-sanity";

export const getDesktopDataQuery = groq`
  {
    "page": *[_type == "page" && slug[0].value.current == $slug][0] {
      _id,
      _type,
      title,
      slug,
      pageBuilder[] {
        _key,
        _type,
        _type == "herosection" => {
          headline,
          tagline,
          image->{
            asset->{
              url,
              altText
            },
            altText,
            caption
          },
          ctaButtons,
          pretitle,
          pretitleLink
        },
        _type == "socialproofsection" => {
          title,
          logos[]->{
            name,
            logo,
            altText,
            url
          }
        },
        _type == "featuressection" => {
          title,
          description,
          features
        },
        _type == "quotesection" => {
          quote,
          authorName,
          authorTitle,
          authorImage
        },
        _type == "metricssection" => {
          title,
          description,
          pretitle,
          image,
          metrics
        },
        _type == "ctasection" => {
          title,
          description,
          ctaButtons
        }
      }
    },
    "siteSettings": *[_type == "siteSettings"][0] {
      siteName,
      siteDescription,
      header->{
        logo->{
          name,
          logo,
          altText,
          url
        }
      },
      footer->{
        linkColumns[]->{
          title,
          links[]->{
            label,
            link
          }
        },
        logo->{
          name,
          logo,
          altText,
          url
        }
      }
    }
  }
`;
