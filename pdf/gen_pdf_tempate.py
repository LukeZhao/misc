def test_pdf():

    con = Consultation.objects(id='5852dc096660f4150c3fe0e5').first()
    template = '/home/lzhao/test_template.html'
    html_str = render_template(template, **{'consultation': con})
    css = CSS('templates/{}/{}/consultation-doctor.css'.format(current_customer, locale))
    doc = HTML(string=html_str).render(stylesheets=[css])
    pages = [page for page in doc.pages]
    if pages:
        pdf = doc.copy(pages).write_pdf()
        ff = open('/home/lzhao/test_pdf.pdf', 'w')
        ff.write(pdf)
        ff.close()