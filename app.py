import re
import torch
from pydantic import BaseModel
from fastapi import FastAPI , Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from transformers import T5ForConditionalGeneration , T5Tokenizer


# initialize our fastapi app
app = FastAPI(title="Text Summarizer App",description="Text Summarization using T5",version="1.0")
app.mount("/static",StaticFiles(directory="static"),name="static") 

# model and Tokenizer
model = T5ForConditionalGeneration.from_pretrained("./saved_summary_model")
tokenizer = T5Tokenizer.from_pretrained("./saved_summary_model")

# as we don't have gpu and mps 
device = torch.device("cpu")

model.to(device)

# templating 
templates = Jinja2Templates(directory="templates") # index.html

# input schemas for dialogue ==> string  using pydantic 
class DialogueInput(BaseModel):
    dialogue:str

def clean_data(text):
    # removing new lines
    text = re.sub(r'\r\n'," ",text)
    # removing extra spaces 
    text = re.sub(r'\s+'," ",text)
    # removing html tags
    text = re.sub(r'<.*?>'," ",text)
    # stripping and lower casing the text
    text = text.strip().lower()
    # return the clean text
    return text

def dialogue_summary(dialogue:str)->str:
    dialogue = clean_data(dialogue)

    # tokens - 1.input ids  2. attention_mask
    inputs = tokenizer(
        dialogue,
        padding="max_length",
        max_length=512,
        trunaction=True,
        return_tensors="pt"
    ).to(device)

    # inputs = {"input_ids":[......] , "attention_mask":[.......]}

    # model generate some target ids 
    targets = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=150,
        num_beams=4,
        early_stopping=True
    )

    # decoding the output 
    summary = tokenizer.decode(targets[0],skip_special_tokens=True)
    return summary 

# Api endpoints
@app.get("/",response_class=HTMLResponse)
async def summary_page(request:Request):
    return templates.TemplateResponse(name="index.html", request=request)

@app.post("/summary/")
async def summarize(dialogue_input:DialogueInput):
    summary = dialogue_summary(dialogue_input.dialogue)
    return {"summary":summary} # json format

