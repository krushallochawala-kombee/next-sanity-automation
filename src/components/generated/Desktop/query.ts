import { groq } from 'next-sanity';

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
          image { value { asset->{url, altText} } },
          ctaButtons[] {
            _key,
            label,
            link {
              externalUrl,
              internalLink->{ slug }
            }
          }
        },
        _type == "socialproofsection" => {
          title,
          description,
          logos[]->{
            _id,
            _type,
            name,
            logo { value { asset->{url, altText} } },
            altText,
            url
          }
        },
        _type == "featuressection" => {
          title,
          description,
          features[]->{
            _id,
            _type,
            title,
            description,
            icon { value { asset->{url, altText} } }
          }
        },
        _type == "quotesection" => {
          quote,
          authorName,
          authorTitle,
          authorImage { value { asset->{url, altText} } }
        },
        _type == "metricssection" => {
          title,
          description,
          metrics[] {
            _key,
            _type,
            value,
            label,
            icon { value { asset->{url, altText} } }
          }
        },
        _type == "ctasection" => {
          title,
          description,
          image { value { asset->{url, altText} } },
          button {
            _key,
            _type,
            label,
            link {
              externalUrl,
              internalLink->{ slug }
            }
          }
        },
        _type == "imagewithalt" => { // Added for the whiteboard image in Metrics section
          image { value { asset->{url, altText} } },
          altText,
          caption
        }
      }
    },
    "header": *[_type == "header"][0] {
      _id,
      _type,
      // Assuming these fields exist in the Header schema based on design
      logo->{ // Reference to Companylogo
        _id,
        _type,
        name,
        logo { value { asset->{url, altText} } },
        altText,
        url
      },
      mainNavigation[] { // Array of Link objects
        _key,
        _type,
        label,
        link {
          externalUrl,
          internalLink->{ slug }
        }
      },
      ctaButton { // Single Button object
        _key,
        _type,
        label,
        link {
          externalUrl,
          internalLink->{ slug }
        }
      }
    },
    "footer": *[_type == "footer"][0] {
      _id,
      _type,
      linkColumns[] {
        _key,
        _type,
        title,
        links[] {
          _key,
          _type,
          label,
          link {
            externalUrl,
            internalLink->{ slug }
          }
        }
      },
      // Assuming these fields exist in the Footer schema based on design
      logo->{ // Reference to Companylogo
        _id,
        _type,
        name,
        logo { value { asset->{url, altText} } },
        altText,
        url
      },
      copyrightText // Internationalized string for copyright
    },
    "siteSettings": *[_type == "siteSettings"][0] {
      siteName,
      siteDescription
    }
  }
`;