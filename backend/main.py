from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import openai
import anthropic
from dotenv import load_dotenv
import base64
from PIL import Image
import io
import requests
import json
from datetime import datetime

load_dotenv()

app = FastAPI()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# 数据存储目录
DATA_DIR = "synthesized_data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_model_client(model: str):
    if model.startswith("gpt"):
        return openai.OpenAI(api_key=OPENAI_API_KEY)
    elif model == "claude":
        return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    else:
        raise HTTPException(status_code=400, detail="Unsupported model")

@app.post("/chat")
async def chat(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    api_key = authorization.split(" ")[1]
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required")

    try:
        message = request.get("message")
        model = request.get("model", "gpt-4")
        multimodal = request.get("multimodal", True)

        client = get_model_client(model)
        
        if model.startswith("gpt"):
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": message}]
            )
            return {"response": response.choices[0].message.content}
        
        elif model == "claude":
            response = client.messages.create(
                model="claude-2",
                messages=[{"role": "user", "content": message}]
            )
            return {"response": response.content[0].text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render")
async def render_image(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        image_data = request.get("image")
        model = request.get("model", "gpt-4")
        prompt = request.get("prompt", "")
        
        # 解码base64图片
        image_data = image_data.split(",")[1]  # 移除data:image/jpeg;base64,前缀
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # 根据选择的模型处理图片
        if model.startswith("gpt"):
            # 使用OpenAI的DALL-E进行图像处理
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.images.edit(
                image=io.BytesIO(image_bytes),
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            rendered_image_url = response.data[0].url
            
        elif model == "claude":
            # 使用Claude进行图像分析
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": f"请分析这张图片并回答：{prompt}"
                            }
                        ]
                    }
                ]
            )
            return {
                "textResponse": response.content[0].text
            }
        
        # 下载处理后的图片
        if rendered_image_url:
            response = requests.get(rendered_image_url)
            rendered_image = Image.open(io.BytesIO(response.content))
            
            # 转换为base64
            buffered = io.BytesIO()
            rendered_image.save(buffered, format="PNG")
            rendered_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return {
                "renderedImage": f"data:image/png;base64,{rendered_base64}",
                "textResponse": f"图片已根据提示词 '{prompt}' 进行处理"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
async def synthesize_data(
    request: dict,
    authorization: Optional[str] = Header(None)
):
    try:
        data_source = request.get("dataSource")
        count = request.get("count")
        filename = request.get("filename")

        if not all([data_source, count, filename]):
            raise HTTPException(status_code=400, detail="Missing required parameters")

        # 生成示例数据
        synthesized_data = []
        for i in range(count):
            item = {
                "id": i + 1,
                "source": data_source,
                "timestamp": datetime.now().isoformat(),
                "value": f"Sample data {i + 1}"
            }
            synthesized_data.append(item)

        # 保存数据到文件
        output_path = os.path.join(DATA_DIR, f"{filename}.json")
        with open(output_path, "w") as f:
            json.dump(synthesized_data, f, indent=2)

        return {
            "message": f"Successfully synthesized {count} data points from {data_source}",
            "file_path": output_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 