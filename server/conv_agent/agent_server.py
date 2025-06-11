import uvicorn
import tomllib

from fastapi import FastAPI, Request
from fastapi.responses import Response
from pydantic import BaseModel

from methods import narrative_elicitation


app = FastAPI(description="")


data = {}

@app.on_event('startup')
def init_data():
    with open('config.toml', "rb") as f:
        config = tomllib.load(f)

    if config["scripted"]["scripted"] == True:
        data['scripted_url'] = config["scripted"]["scripted_url"] + "conf=" + config["scripted"]["conf"]
        data['scripted'] = True

    else:
        data['scripted'] = False
        pipeline, tokenizer, history = narrative_elicitation.get_pipeline(config)

        data['pipeline'] = pipeline
        data['tokenizer'] = tokenizer
        data['history'] = history
    
    return data



class AgentResponse(BaseModel):
    model_out: str
    class Config:
        schema_extra = {
            "example": {
                "model_out" : "Hello"
                }
        }


@app.post('/elicit-question', response_model=AgentResponse)
async def elicit(request: Request):
    request_data = await request.json()

    if data['scripted']:
        model_out = narrative_elicitation.get_scripted(request_data['narrative'], data['scripted_url'])
    else:
        nar = request_data['narrative']

        model_out = narrative_elicitation.model_response(data['pipeline'],data['tokenizer'], nar, data['history'])

    print(model_out)
    return {"model_out": model_out}


if __name__ == "__main__":
    with open('config.toml', "rb") as f:
        config = tomllib.load(f)

    uvicorn.run(
        "__main__:app",
        host=config["server"]["self_host"],
        port=config["server"]["self_port"],
        reload=True,
        workers=4
    )
