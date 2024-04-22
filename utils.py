# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
from pypdf import PdfReader
import pandas as pd
import re
from langchain_community.chat_models import ChatOpenAI

# from langchain.llms.openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text, Number

###########################
# To read the PDF
import PyPDF2
# To analyze the PDF layout and extract text
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# To extract text from tables in PDF
import pdfplumber
# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path
# To perform OCR to extract text from images 
import pytesseract 
# To remove the additional created files
import os

def text_extraction(element):
    # Extracting the text from the in-line text element
    line_text = element.get_text()
    
    # Find the formats of the text
    # Initialize the list with all the formats that appeared in the line of text
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # Iterating through each character in the line of text
            for character in text_line:
                if isinstance(character, LTChar):
                    # Append the font name of the character
                    line_formats.append(character.fontname)
                    # Append the font size of the character
                    line_formats.append(character.size)
    # Find the unique font sizes and names in the line
    format_per_line = list(set(line_formats))
    
    # Return a tuple with the text in each line along with its format
    return (line_text, format_per_line)

# Create a function to crop the image elements from PDFs
def crop_image(element, pageObj):
    # Get the coordinates to crop the image from the PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    # Crop the page using coordinates (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Save the cropped page to a new PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Save the cropped PDF to a new file
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# Create a function to convert the PDF to images
def convert_to_images(input_file,):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")

# Create a function to read text from images
def image_to_text(image_path):
    # Read the image
    img = Image.open(image_path)
    # Extract the text from the image
    text = pytesseract.image_to_string(img)
    return text

# Extracting tables from the page

def extract_table(pdf_path, page_num, table_num):
    # Open the pdf file
    pdf = pdfplumber.open(pdf_path)
    # Find the examined page
    table_page = pdf.pages[page_num]
    # Extract the appropriate table
    table = table_page.extract_tables()[table_num]
    return table

# Convert table into the appropriate format
def table_converter(table):
    table_string = ''
    # Iterate through each row of the table
    for row_num in range(len(table)):
        row = table[row_num]
        # Remove the line breaker from the wrapped texts
        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        # Convert the table into a string 
        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
    # Removing the last line break
    table_string = table_string[:-1]
    return table_string


def extract_pdf_content(pdf_path):
    # Find the PDF path
    # pdf_path = 'OFFER 3.pdf'

    # create a PDF file object
    
    pdfFileObj = open(pdf_path, 'rb')
    # create a PDF reader object
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # Create the dictionary to extract text from each image
    text_per_page = {}
    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        
        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        # Initialize the number of the examined tables
        table_num = 0
        first_element= True
        table_extraction_flag= False
        # Open the pdf file
        pdf = pdfplumber.open(pdf_path)
        # Find the examined page
        page_tables = pdf.pages[pagenum]
        # Find the number of tables on the page
        tables = page_tables.find_tables()


        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the elements as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # Find the elements that composed a page
        for i,component in enumerate(page_elements):
            # Extract the position of the top side of the element in the PDF
            pos= component[0]
            # Extract the element of the page layout
            element = component[1]
            
            # Check if the element is a text element
            if isinstance(element, LTTextContainer):
                # Check if the text appeared in a table
                if table_extraction_flag == False:
                    # Use the function to extract the text and format for each text element
                    (line_text, format_per_line) = text_extraction(element)
                    # Append the text of each line to the page text
                    page_text.append(line_text)
                    # Append the format for each line containing text
                    line_format.append(format_per_line)
                    page_content.append(line_text)
                else:
                    # Omit the text that appeared in a table
                    pass

            # Check the elements for images
            if isinstance(element, LTFigure):
                # Crop the image from the PDF
                crop_image(element, pageObj)
                # Convert the cropped pdf to an image
                convert_to_images('cropped_image.pdf')
                # Extract the text from the image
                image_text = image_to_text('PDF_image.png')
                text_from_images.append(image_text)
                page_content.append(image_text)
                # Add a placeholder in the text and format lists
                page_text.append('image')
                line_format.append('image')

            # Check the elements for tables
            if isinstance(element, LTRect):
                # If the first rectangular element
                if first_element == True and (table_num+1) <= len(tables):
                    # Find the bounding box of the table
                    lower_side = page.bbox[3] - tables[table_num].bbox[3]
                    upper_side = element.y1 
                    # Extract the information from the table
                    table = extract_table(pdf_path, pagenum, table_num)
                    # Convert the table information in structured string format
                    table_string = table_converter(table)
                    # Append the table string into a list
                    text_from_tables.append(table_string)
                    page_content.append(table_string)
                    # Set the flag as True to avoid the content again
                    table_extraction_flag = True
                    # Make it another element
                    first_element = False
                    # Add a placeholder in the text and format lists
                    page_text.append('table')
                    line_format.append('table')

                # Check if we already extracted the tables from the page
                if element.y0 >= lower_side and element.y1 <= upper_side:
                    pass
                elif not isinstance(page_elements[i+1][1], LTRect):
                    table_extraction_flag = False
                    first_element = True
                    table_num+=1


    # Create the key of the dictionary
    dctkey = 'Page_'+str(pagenum)
    # Add the list of list as the value of the page key
    text_per_page[dctkey]= [page_text, line_format, text_from_images,text_from_tables, page_content]

    # Closing the pdf file object
    pdfFileObj.close()

    # Deleting the additional files created
    os.remove('cropped_image.pdf')
    os.remove('PDF_image.png')

    # Display the content of the page
    result = ''.join(text_per_page['Page_0'][4])
    processed_text = " ".join(result.split("\n"))
    # print(result)
    return processed_text


###########################
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    processed_text = " ".join(text.split("\n"))
    
    return processed_text

def extract_data(processed_text):
    
    # template = '''Extract all following values: invoice no., Description, 
    # Quantity, date, Unit price, Amount, Total,
    # email, phone number and address from this data: {pages}
    
    # Expected output : remove any dollar symbols {{'Invoice no.':'1001329', 
    # 'Description':'Office Chair', 'Quantity':'2', 'Date':'05/01/2022', 
    # 'Unit price':'1100.00', Amount':'2200.00', 'Total':'2200.00',
    # 'email':'santoshverma0988@gmail.com', 'phone number':'9999999999',
    # 'Address':'Mumbai, India'}}
    # '''
    invoice_schema1 = Object(
        id="invoice_extraction",
        description="extraction of relevant information from invoice",
        attributes=[
            Text(
                id="invoice_number",
                description= "unique number (identifier) of given invoice",
            examples=[
                ("Invoice Number: INV-23490", "INV-23490"),
                ("INVNO-76890", "INVNO-76890"),
                ("Invoice: INV-100021", "INV-100021"),
                ("Bill No:123", "123")
            ])
        ],
        many=True,
    )
    
    billing_address_schema = Object(
    id="address",
    description="address details",
    attributes=[
        Text(id="name", description="the name of person and organization"),
        Text(id="address_line", description="the local delivery information such as street, building number, PO box, or apartment portion of a postal address"),
        Text(id="city", description="the city portion of the address"),
        Text(id="state_province_code", description="the code for address US states"),
        Text(id="email", description="mail id of the person"),
        Number(id="contact", description="contact number of the person"),
        Number(id="postal_code", description="the postal code portion of the address")
    ],
    examples=[
        (
            "James Bond, Bond Industries 5000 Forbes Avenue Pittsburgh, PA 15213",
            {
                "name": "James Bond, Bond Industries",
                "address_line": "Bond Industries 5000 Forbes Avenue",
                "city": "Pittsburgh",
                "state_province_code": "PA",
                "email": "abc@company.com",
                "contact": "9980247907",
                "postal_code": "15213",
            },
        ),
        (
            "Kaushik Shakkari 840 Childs Way, Los Angeles, CA 90089",
            {
                "name": "Kaushik Shakkari",
                "address_line": "840 Childs Way",
                "city": "Los Angeles",
                "state_province_code": "CA",
                "email": "abc@company.com",
                "contact": "12963869",
                "postal_code": "90089",
            },
        ),
        
       (
            "Shakkari Solutions PO Box 1234 Atlanta GA 30033",
            {
                "name": "Shakkari Solutions",
                "address_line": "PO Box 1234",
                "city": "Atlanta",
                "state_province_code": "GA",
                "email": "abc@company.in",
                "contact": "8524968510",
                "postal_code": "30033",
            },
        ) 
    ],
    many=False,
    )  
    
    products_schema = Object(
    id="bill",
    description="the details of bill",
    attributes=[
        Text(id="product_description", description="the description of the product or service"),
        Text(id="count", description="number of units bought for the product"),
        Text(id="unit_item_price", description="price per unit"),
        Text(id="product_total_price", description="the total price, which is number of units * unit_price"),
    ],
    examples=[
        (
            "iphone 14 pro black 2 $1200.00 $2400.00",
            {
                "product_description": "iphone 14 pro black",
                "count": 2,
                "unit_item_price": 1200,
                "product_total_price": 2400,
            },
        ),
    ],
    many=False
    )

    total_bill_schema = Object(
    id="total_bill",
    description="the details of total amount, discounts and tax",
    attributes=[
        Number(id="total", description="the total amount before tax and delivery charges"),
        Number(id="discount_amount", description="discount amount is total cost * discount %"),
        Number(id="tax_amount", description="tax amount is tax_percentage * (total - discount_amount). If discount_amount is 0, then its tax_percentage * total"),
        Number(id="delivery_charges", description="the cost of shipping products"),
        Number(id="final_total", description="the total price or balance after removing tax, adding delivery and tax from total"),
    ],
    examples=[
        (
            "total $100000.00 discount 0% tax 5 percentage delivery cost $100.00 final_total $95100.00",
            {
                "total": 100000,
                "discount_amount": 0,
                "tax_amount": 5000,
                "delivery_charges": 100,
                "final_total": 105100
            },
        ),
    ],
    many=False
    )
    
    invoice_schema = Object(
    id="invoice_information",
    description="relevant invoice parsing from raw extracted text",
    attributes=[
        Text(id="invoice_number", description= "unique number (identifier) of given invoice",
        examples=[
            ("Invoice Number: INV-23490", "INV-23490"),
            ("INVNO-76890", "INVNO-76890"),
            ("Invoice: INV-100021", "INV-100021")
            
        ]),
        # invoice_schema1,
        billing_address_schema,
        total_bill_schema,
        products_schema,
    ],
    many=True,
    )
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=2000)

    invoice_chain = create_extraction_chain(llm, invoice_schema,encoder_or_encoder_class="json")
    
    full_response = invoice_chain.run(text=processed_text)['data']
    
    #output
    
    # prompt_template = ChatPromptTemplate(input_variables=['pages'], template=template)

    # llm = OpenAI(model="gpt-3.5-turbo-instruct" ,temperature=0.4)
    
    # full_response = llm(prompt_template.format(pages=pages_data))

    return full_response

def create_docs(invoiceDir):
    
    df = pd.DataFrame({'invoice_number': pd.Series(dtype='str'),
                   'name': pd.Series(dtype='str'),
                   'address_line': pd.Series(dtype='str'),
                   'state_province_code': pd.Series(dtype='str'),
	                'postal_code': pd.Series(dtype='str'),
                   'total_bill': pd.Series(dtype='int'),
                   'product_description': pd.Series(dtype='str'),
                   'unit_item_price': pd.Series(dtype='str'),
	                'product_total_price': pd.Series(dtype='str'),
                    "total" : pd.Series(dtype='str'),
                    "discount_amount" : pd.Series(dtype='str'),
                    "tax_amount" : pd.Series(dtype='str'),
                    "delivery_charges" : pd.Series(dtype='str'),
                    "final_total" : pd.Series(dtype='str')
                    })
    df_json_metadata = pd.DataFrame(columns=['Filename','Invoice_Metadata'])
    # llm_extracted_data_list = []
    df_raw_text = pd.DataFrame(columns=['Filename','Raw_Text'])
    for file in os.listdir(invoiceDir):
        if file.endswith(".pdf"):
            # raw_data=get_pdf_text(filename)
            raw_data = extract_pdf_content(invoiceDir + "/" + file)
            text_new_row = {'Filename':file, 'Raw_Text':raw_data}
            df_raw_text.loc[len(df_raw_text)] = text_new_row

            llm_extracted_data=extract_data(raw_data)
            # llm_extracted_data_list.append(llm_extracted_data)
            new_row = {'Filename':file, 'Invoice_Metadata':llm_extracted_data}
            df_json_metadata.loc[len(df_json_metadata)] = new_row
    # for i in range(len(raw_data_list)):
    # for llm_extracted_data in llm_extracted_data_list:
    #     print(llm_extracted_data)
    #     print("#########")
    #     invoice_number = llm_extracted_data["invoice_information"][0]["invoice_number"]
    #     # for address_field in llm_extracted_data["invoice_information"][0]["address"]:
    #     name = llm_extracted_data["invoice_information"][0]["address"]["name"]
    #     address_line = llm_extracted_data["invoice_information"][0]["address"]["address_line"]
    #     state_province_code = llm_extracted_data["invoice_information"][0]["address"]["state_province_code"]
    #     postal_code = llm_extracted_data["invoice_information"][0]["address"]["postal_code"]
        
    #     # for address_field in llm_extracted_data["invoice_information"][0]["total_bill"]:
    #     total = llm_extracted_data["invoice_information"][0]["total_bill"]["total"]
    #     discount_amount = llm_extracted_data["invoice_information"][0]["total_bill"]["discount_amount"]
    #     tax_amount = llm_extracted_data["invoice_information"][0]["total_bill"]["tax_amount"]
    #     delivery_charges = llm_extracted_data["invoice_information"][0]["total_bill"]["delivery_charges"]
    #     final_total = llm_extracted_data["invoice_information"][0]["total_bill"]["final_total"]

    #     # for address_field in llm_extracted_data["invoice_information"][0]["bill"]:
    #     product_description = llm_extracted_data["invoice_information"][0]["bill"]["product_description"]
    #     count = llm_extracted_data["invoice_information"][0]["bill"]["count"]
    #     unit_item_price = llm_extracted_data["invoice_information"][0]["bill"]["unit_item_price"]
    #     product_total_price = llm_extracted_data["invoice_information"][0]["bill"]["product_total_price"]
        
    #     new_row = {'invoice_number':invoice_number, 'name': name, 'address_line': address_line, 'state_province_code': state_province_code,'postal_code':postal_code, \
    #             "product_description":product_description,"count":count,"unit_item_price":unit_item_price,"product_total_price":product_total_price,\
    #                 "total":total,"discount_amount":discount_amount,"tax_amount":tax_amount,"delivery_charges":delivery_charges,"final_total":final_total}
    #     df.loc[len(df)] = new_row

    # df.head()
    return df_json_metadata, df_raw_text