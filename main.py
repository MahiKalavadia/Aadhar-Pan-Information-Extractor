from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
import os, json
from encoder import encode_image
from validators import valid_aadhar, valid_pan

load_dotenv()

app = FastAPI(
    title="Extract Information from Image",
    description="A simple application that extract personal details from Aadhar card or PAN card.",
    version="1.0.0"
)

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("API key is not accessible. Check API key!")

client = Groq(api_key=api_key)

origins = [
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)
   
@app.post('/information')
async def extract_info(image: UploadFile = File(...)):
    image1 = await encode_image(image)

    prompt = """Things to perform: Analyze the image and extract
    "Name": "full name from the uploaded image ad extract only the full name whose pan card it is dont include fathers name"
    "DOB": "DOB/date of birth from the uploaded image"
    "Gender": "gender from the uploaded image and if the image hasn't mentioned gender then look at the photo in the uploaded image and identify gender as Male or Female."
    "Aadhar Number or PAN Number": "Aadhar number if aadhar card uploaded or PAN number if PAN Card uploaded."

    Always have DOB in this format: DD/MM/YYYY
    Always write gender in this format: Male or Female
    Always have Aadhar Card number in this format: XXXX XXXX XXXX where X represents the digits you extracted from the image
    ALways keep PAN Number as it is after extraction make sure that PAN number format is as AAAAAXXXXA where A represents alphabets and X represents digits and make sure A is all capital

    If it is aadhar number then print in output Aadhar Number
    If it is PAN number then print in output PAN Number and no space between PAN number
    Instruction: Never include any piece of extra information except those 4 fields 

    """
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",

        messages=[{
            "role":"user",
            "content": [
                {
                    "type":"text",
                    "text": prompt
                },
                {
                    "type":"image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image1}"
                    }
                    
                }
            ]
        }],
        response_format={
            "type":"json_schema",
            "json_schema":{
                "name":"extract_info",
                "schema":{
                    "type":"object",
                    "properties":{
                        "Name": {"type":"string"},
                        "DOB":{"type":"string"},
                        "Gender":{"type":"string"},
                        "Aadhar Number":{"type":"string"},
                        "PAN Number":{"type":"string"}
                    },
                    "required": ["Name","DOB","Gender","Aadhar Number","PAN Number"],
                    "additionalProperties":False
                }

            }
        },
        temperature=1,
        top_p=1,
        stream=False
    )

    result = json.loads(response.choices[0].message.content or "{}")
        
    aadhar = result.get("Aadhar Number")
    pan = result.get("PAN Number")

    if aadhar:
        if not valid_aadhar(aadhar): 
            return {"error":"Invalid Aadhar number extracted. Please retry with a clearer image."}
    elif pan:
        if not valid_pan(pan):
            return {"error":"Invalid PAN number extracted. Please retry with a clearer image."}
    else:
        return {"error":"Neither Aadhar nor PAN was extracted. Please try again with a clearer image."}
    
    return result
