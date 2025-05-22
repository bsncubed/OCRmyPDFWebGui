# OCRmyPDFWebGui
A Web UI for OCR My PDF. 

## Dependicies
TBC
- OCRmyPDF
- Pyton 3

## Docker
Last image generatoed on 18-3-25
This image has OCRmyPDF running as well (Verserion X.XX)

### Docker Compose
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
- [ ] Docker: Make image smaller
- [ ] Docker: Move away from a python development server
- [ ] Create favicon
- [ ] Audomated image and container buildign pipeline
- [ ] Dependincy upgrade automation pipeline
- [ ] Update documetation for Envrioment varables
- [ ] Fix Spelling
