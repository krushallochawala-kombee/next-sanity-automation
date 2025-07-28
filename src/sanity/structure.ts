import { StructureResolver } from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('Content')
    .items([
      // Global Documents
    S.listItem()
      .title('Footer')
      .id('footer')
      .child(
        S.document()
          .schemaType('footer')
          .documentId('footer')
      ),
    S.listItem()
      .title('Header')
      .id('header')
      .child(
        S.document()
          .schemaType('header')
          .documentId('header')
      ),
    S.listItem()
      .title('Site Settings')
      .id('siteSettings')
      .child(
        S.document()
          .schemaType('siteSettings')
          .documentId('siteSettings')
      ),
      
      // Divider
      S.divider(),
      
      // Regular Documents
    S.documentTypeListItem('companylogo').title('Companylogo'),
    S.documentTypeListItem('feature').title('Feature'),
    S.documentTypeListItem('metric').title('Metric'),
    S.documentTypeListItem('page').title('Page'),
    ])
