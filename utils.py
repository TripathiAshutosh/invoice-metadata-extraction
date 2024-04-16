# from langchain.llms import OpenAI
from langchain_community.llms import OpenAI
from pypdf import PdfReader
import pandas as pd
import re
from langchain.chat_models import ChatOpenAI
# from langchain.llms.openai import OpenAI
from langchain.prompts import ChatPromptTemplate
from kor.extraction import create_extraction_chain
from kor.nodes import Object, Text, Number


def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    print("#################3",text)
    processed_text = " ".join(text.split("\n"))
    print("#################3",processed_text)
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
    invoice_schema = Object(
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
        many=False,
    )
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=2000)

    invoice_chain = create_extraction_chain(llm, invoice_schema)
    
    full_response = invoice_chain.run(text=processed_text)['data']
    print(full_response)
    #output
    
    # prompt_template = ChatPromptTemplate(input_variables=['pages'], template=template)

    # llm = OpenAI(model="gpt-3.5-turbo-instruct" ,temperature=0.4)
    
    # full_response = llm(prompt_template.format(pages=pages_data))

    return full_response

def create_docs(user_pdf_list):
    
    df = pd.DataFrame({'Invoice no.': pd.Series(dtype='str'),
                   'Description': pd.Series(dtype='str'),
                   'Quantity': pd.Series(dtype='str'),
                   'Date': pd.Series(dtype='str'),
	                'Unit price': pd.Series(dtype='str'),
                   'Amount': pd.Series(dtype='int'),
                   'Total': pd.Series(dtype='str'),
                   'Email': pd.Series(dtype='str'),
	                'Phone number': pd.Series(dtype='str'),
                   'Address': pd.Series(dtype='str')
                    })

    for filename in user_pdf_list:
        
        print(filename)
        raw_data=get_pdf_text(filename)
        #print(raw_data)
        #print("extracted raw data")

        llm_extracted_data=extract_data(raw_data)
        #print("llm extracted data")
        #Adding items to our list - Adding data & its metadata

    #     pattern = r'{(.+)}'
    #     match = re.search(pattern, llm_extracted_data, re.DOTALL)

    #     if match:
    #         extracted_text = match.group(1)
    #         # Converting the extracted text to a dictionary
    #         data_dict = eval('{' + extracted_text + '}')
    #         print(data_dict)
    #     else:
    #         print("No match found.")

        
    #     df=df.append([data_dict], ignore_index=True)
    #     print("********************DONE***************")
    #     #df=df.append(save_to_dataframe(llm_extracted_data), ignore_index=True)

    # df.head()
    return llm_extracted_data #df