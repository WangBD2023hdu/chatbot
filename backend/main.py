from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import requests
import base64
import io
import os
from typing import Optional, Dict, List
import json
from datetime import datetime, timedelta

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# 存储聊天消息的缓存
chat_messages_cache: Dict[str, List[Dict]] = {}
CACHE_EXPIRY = timedelta(minutes=30)  # 缓存过期时间

# 清理过期缓存的函数
def cleanup_expired_cache():
    current_time = datetime.now()
    expired_keys = []
    for key, value in chat_messages_cache.items():
        if current_time - value['timestamp'] > CACHE_EXPIRY:
            expired_keys.append(key)
    for key in expired_keys:
        del chat_messages_cache[key]

# Template configurations
TEMPLATE_PROMPTS = {
    "template1": {
        "gpt": "Create a professional business image with the following elements: {prompt}",
        "claude": "Analyze this image from a business perspective: {prompt}"
    },
    "template2": {
        "gpt": "Create an artistic painting with the following elements: {prompt}",
        "claude": "Analyze this image from an artistic perspective: {prompt}"
    },
    "template3": {
        "gpt": "Create a modern minimalist design with the following elements: {prompt}",
        "claude": "Analyze this image from a minimalist perspective: {prompt}"
    }
}

# Authorization dependency
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization.split(" ")[1]

@app.post("/chat")
async def chat(message: dict, authorization: str = Depends(verify_token)):
    try:
        model = message.get("model", "gpt-4")
        multimodal = message.get("multimodal", True)
        text = message.get("text", "")
        image = message.get("image", None)
        
        # 清理过期缓存
        cleanup_expired_cache()
        
        # 存储聊天消息
        token = authorization.split(" ")[1]
        if token not in chat_messages_cache:
            chat_messages_cache[token] = {
                'messages': [],
                'timestamp': datetime.now()
            }
        
        # 添加用户消息
        chat_messages_cache[token]['messages'].append({
            'type': 'user',
            'text': text,
            'image': image,
            'timestamp': datetime.now()
        })
        
        if model == "gpt-4":
            # OpenAI API call
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": text}]
            }
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            response_text = response.json()["choices"][0]["message"]["content"]
            
        elif model == "claude":
            # Anthropic API call
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "prompt": f"\n\nHuman: {text}\n\nAssistant:",
                "max_tokens_to_sample": 1000
            }
            response = requests.post(
                "https://api.anthropic.com/v1/complete",
                headers=headers,
                json=data
            )
            response_text = response.json()["completion"]
        
        # 添加助手响应
        chat_messages_cache[token]['messages'].append({
            'type': 'assistant',
            'text': response_text,
            'timestamp': datetime.now()
        })
        
        return {
            "response": response_text,
            "messageId": len(chat_messages_cache[token]['messages']) - 1
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), authorization: str = Depends(verify_token)):
    try:
        # Save file to temporary location
        file_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        return {"fileUrl": f"/files/{file.filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-image")
async def upload_image(image: UploadFile = File(...), authorization: str = Depends(verify_token)):
    try:
        # Save image to temporary location
        image_path = f"uploads/{image.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
            
        return {"imageUrl": f"/images/{image.filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/render")
async def render_image(request: dict, authorization: str = Depends(verify_token)):
    try:
        image_data = request.get("image")
        model = request.get("model", "gpt-4")
        prompt = request.get("prompt", "")
        template = request.get("template", "template1")
        token = authorization.split(" ")[1]

        if not image_data:
            raise HTTPException(status_code=400, detail="No image provided")
        
        # 检查是否有聊天历史
        if token not in chat_messages_cache or not chat_messages_cache[token]['messages']:
            raise HTTPException(
                status_code=400, 
                detail="No chat history found. Please send a message first."
            )
        
        # 获取最近的聊天消息
        recent_messages = chat_messages_cache[token]['messages'][-5:]  # 获取最近5条消息
        chat_context = "\n".join([
            f"{'User' if msg['type'] == 'user' else 'Assistant'}: {msg['text']}"
            for msg in recent_messages
        ])
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(",")[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Process image based on model and template
        if model == "gpt-4":
            # 使用聊天上下文增强提示
            enhanced_prompt = f"Chat Context:\n{chat_context}\n\nBased on the above context, {TEMPLATE_PROMPTS[template]['gpt'].format(prompt=prompt)}"
            
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "prompt": enhanced_prompt,
                "n": 1,
                "size": "1024x1024"
            }
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data
            )
            rendered_image = response.json()["data"][0]["url"]
            
        elif model == "claude":
            # 使用聊天上下文进行分析
            analysis_prompt = f"Chat Context:\n{chat_context}\n\nBased on the above context, {TEMPLATE_PROMPTS[template]['claude'].format(prompt=prompt)}"
            
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "prompt": f"\n\nHuman: {analysis_prompt}\n\nAssistant:",
                "max_tokens_to_sample": 1000
            }
            response = requests.post(
                "https://api.anthropic.com/v1/complete",
                headers=headers,
                json=data
            )
            text_response = response.json()["completion"]
            
            # Return original image with analysis
            return {
                "renderedImage": image_data,
                "textResponse": text_response
            }
            
        return {
            "renderedImage": rendered_image,
            "textResponse": f"Image rendered using {template} template with context from chat history"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
async def synthesize_data(request: dict, authorization: str = Depends(verify_token)):
    try:
        language = request.get("language", "en")
        scene = request.get("scene", "business")
        count = request.get("count", 100)
        filename = request.get("filename", "synthesized_data")
        
        # Generate synthetic data based on parameters
        # This is a placeholder - implement your actual data synthesis logic
        synthetic_data = {
            "language": language,
            "scene": scene,
            "count": count,
            "filename": filename,
            "status": "completed"
        }
        
        # Save to file
        with open(f"outputs/{filename}.json", "w") as f:
            json.dump(synthetic_data, f)
            
        return {
            "message": f"Successfully generated {count} {scene} samples in {language}",
            "data": synthetic_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static file serving endpoints
@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = f"uploads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/images/{filename}")
async def get_image(filename: str):
    image_path = f"uploads/{filename}"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

# 添加代码管理相关的路由
@app.get("/code")
async def get_code():
    try:
        # 从文件系统或数据库获取代码
        css_code = ""
        js_code = ""
        try:
            with open("static/css/custom.css", "r") as f:
                css_code = f.read()
        except FileNotFoundError:
            pass

        try:
            with open("static/js/custom.js", "r") as f:
                js_code = f.read()
        except FileNotFoundError:
            pass

        return {
            "css": css_code,
            "js": js_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/code/css")
async def save_css(code: dict):
    try:
        # 确保目录存在
        os.makedirs("static/css", exist_ok=True)
        
        # 保存 CSS 代码
        with open("static/css/custom.css", "w") as f:
            f.write(code["code"])
        
        return {"message": "CSS code saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/code/js")
async def save_js(code: dict):
    try:
        # 确保目录存在
        os.makedirs("static/js", exist_ok=True)
        
        # 保存 JavaScript 代码
        with open("static/js/custom.js", "w") as f:
            f.write(code["code"])
        
        return {"message": "JavaScript code saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 