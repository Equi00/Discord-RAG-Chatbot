from openai import OpenAI
import os
from dotenv import load_dotenv
from backend.services.conv_service import ConvService

load_dotenv()

ConvService().gpt_response()