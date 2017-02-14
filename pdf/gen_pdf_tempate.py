def test_pdf(con):
    template = 'test_template.html'
    html_str = render_template(template, **{'consultation': con})
    css = CSS('templates/{}/{}/consultation-doctor.css'.format(current_customer, 'en_US'))
    doc = HTML(string=html_str).render(stylesheets=[css])
    pages = [page for page in doc.pages]
    if pages:
        pdf = doc.copy(pages).write_pdf()
        ff = open('/home/lzhao/test_pdf.pdf', 'w')
        ff.write(pdf)
        ff.close()