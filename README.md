# OCRmyPDFWebGui

Last image generatoed on 18-3-25

## Docker Compose
```yaml
services:
  ocr_my_pdf_webui:
    image: ghcr.io/bsncubed/ocrmypdfwebgui:latest
    ports:
      - "5000:5000"
    environment:
      - GUNICORN_TIMEOUT=300
      - TZ=Australia/Sydney
```


## To do
- [ ] Make image smaller
- [ ] Create favicon
- [ ] Dependincy upgrade automation pipeline
- [ ] Update documetation for Envrioment varables
- [ ] Fix Spelling
