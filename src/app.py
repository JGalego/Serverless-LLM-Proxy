r"""
  _____                          _                 _      _      __  __   _____
 / ____|                        | |               | |    | |    |  \/  | |  __ \
| (___   ___ _ ____   _____ _ __| | ___  ___ ___  | |    | |    | \  / | | |__) | __ _____  ___   _
 \___ \ / _ \ '__\ \ / / _ \ '__| |/ _ \/ __/ __| | |    | |    | |\/| | |  ___/ '__/ _ \ \/ / | | |
 ____) |  __/ |   \ V /  __/ |  | |  __/\__ \__ \ | |____| |____| |  | | | |   | | | (_) >  <| |_| |
|_____/ \___|_|    \_/ \___|_|  |_|\___||___/___/ |______|______|_|  |_| |_|   |_|  \___/_/\_\\__, |
                                                                                               __/ |
                                                                                              |___/

OpenAI-compatible proxy on AWS Lambda and Amazon API Gateway powered by LiteLLM
"""

# Standard imports
import os
import logging

from typing import Annotated

# Library ports
import boto3
import uvicorn

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from mangum import Mangum

# LiteLLM imports
import litellm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Initialize app
app = FastAPI(
    title="Serverless LiteLLM Proxy 🚅⚡☁️",
    summary="OpenAI-compatible proxy on AWS Lambda and Amazon API Gateway powered by LiteLLM.",
    version="0.1.0",
    contact={
        "name": "João Galego",
        "url": "https://github.com/JGalego"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
)

##################
# Authentication #
##################

# Initialize SSM client
ssm = boto3.client("ssm")

def list_api_keys():
    """
    Returns a list of API key names.
    """
    response = ssm.describe_parameters(
        ParameterFilters=[{
            'Key': "Name",
            'Option': "BeginsWith",
            'Values': [
                os.environ.get('SERVERLESS_LLM_PROXY_API_KEYS', "ServerlessLLMProxyAPIKey")
            ]
        }]
    )
    api_key_names = [param['Name'] for param in response['Parameters']]

    if len(api_key_names) == 0:
        logging.warning("No API keys found!")

    return [param['Name'] for param in response['Parameters']]

def get_api_key(name: str):
    """
    Returns the value 
    """
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

# Initialize bearer token authN
security = HTTPBearer()

def api_key_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Handles API key authentication. 
    """
    for name in list_api_keys():
        if credentials.credentials == get_api_key(name):
            return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    )

###########
# Routing #
###########

# Initialize router
router = APIRouter(
    dependencies=[Depends(api_key_auth)]
)

# Add proxy routes
@router.post("/chat/completions")
async def completion(request: Request):
    """
    Perform a completion using supported LLMs
    """
    request = await request.json()
    return litellm.completion(**request)

@router.post("/embeddings")
async def embedding(request: Request):
    """
    Generates embeddings for a given input.
    """
    request = await request.json()
    return litellm.embedding(**request)

@router.post("/images/generations")
async def image_generation(request: Request):
    """
    Generates a new image from a prompt.
    """
    request = await request.json()
    return litellm.image_generation(**request)

@app.get("/health")
async def health():
    """For health check, if needed"""
    return {'status': "I'm alive!"}

# Register routes
app.include_router(router, prefix="/api/v1")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

########
# Main #
########

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
