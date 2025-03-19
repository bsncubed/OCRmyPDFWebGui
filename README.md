# OCRmyPDFWebGui

Last image generatoed on 18-3-25

```yaml
services:
  ocr_my_pdf_webui:
    image: gitea.apointless.space/bsncubed/ocrmypdfwebgui:latest
    ports:
      - "5000:5000"
    environment:
      - GUNICORN_TIMEOUT=300
      - TZ=Australia/Sydney
```