Problem Statement: Automate data extraction from invoice pdfs (images) 

Description: Everyday lots of invoices are generated and keeping the record like invoice numbers, buyer details like contact, email, address and other important context-based information is very necessary in today’s data driven world.

When we have quite advanced on data driven decision making and everybody use the phrases like data is the new oil, data is the new gas etc., it is utmost important to analyze every kind of data to do descriptive, prescriptive and predictive analysis and take the business ahead.

That is where there is a need in finance domain as well to analyze the invoice data. However, the challenge here is that those invoices are not in the standard formats and extracting specific contextual information is very challenging.

Solution Proposed: A Gen AI based invoice extractor having two components: 
Prompt
Large Language Model (LLM)
Prompt has metadata templates like Invoice Schema, Address Schema, Product Schema, Bill Schema and LLM accepts this prompt with raw text extracted from pdfs and generate required metadata.

Solution: US-Design

<img width="795" alt="image" src="https://github.com/TripathiAshutosh/invoice-metadata-extraction/assets/40880107/b9082639-de14-47e9-8c87-f915c19ffe81">

<img width="810" alt="image" src="https://github.com/TripathiAshutosh/invoice-metadata-extraction/assets/40880107/4efebf06-7abf-4158-aa17-893af14bfb4b">

<img width="814" alt="image" src="https://github.com/TripathiAshutosh/invoice-metadata-extraction/assets/40880107/7e2dd03a-7216-4fcf-a21c-345491ac411a">

Different Approaches

Optical Character Recognition (OCR)
Natural Language Processing (NLP)
Machine Learning (ML) algorithms
Template-based extraction
Partial RAG based Prompt enabled LLM Powered Invoice extractor

Challenges

Variability in invoice formats and layouts
Poor image quality and resolution
Handwritten text recognition
Language and localization issues
<img width="355" alt="image" src="https://github.com/TripathiAshutosh/invoice-metadata-extraction/assets/40880107/2341c176-d670-41d3-85a1-0073b395ecc0">

Future Roadmap

Development of hybrid approaches combining OCR, NLP, and ML techniques.
Standardization efforts to streamline invoice formats and layouts.
Expansion of multilingual support and language understanding capabilities.
Integration of advanced AI technologies like deep learning for improved accuracy.
![Uploading image.png…]()




#### References

https://towardsdatascience.com/extracting-text-from-pdf-files-with-python-a-comprehensive-guide-9fc4003d517

https://github.com/gkamradt/langchain-tutorials/blob/main/data_generation/Expert%20Structured%20Output%20(Using%20Kor).ipynb

https://blog.gopenai.com/invoice-or-bill-custom-parsing-using-kor-langchain-extension-generative-language-models-prompt-7133193358fa
