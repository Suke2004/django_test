from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChatMessage
from django.http import HttpResponse
import google.generativeai as genai
import requests
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini setup
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

# OpenRouter config
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL")

# Groq config
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_MODEL = os.environ.get("GROQ_MODEL")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

def home(request):
    return HttpResponse("<h1>Welcome to the AI Chatbot Backend</h1><p>Use the <code>/chat/</code> endpoint to talk to the bot.</p>")


class ChatAPIView(APIView):
    def post(self, request):
        print("📥 Incoming POST request to /chat/")
        user_msg = request.data.get("message")
        selected_model = request.data.get("model", "gemini").lower()
        print(f"📝 User message: {user_msg}, model: {selected_model}")

        if not user_msg:
            return Response({"error": "No message provided"}, status=400)

        try:
            # Save user message
            ChatMessage.objects.create(sender="user", message=user_msg)

            if selected_model == "ollama":
                print("🔁 Using Ollama...")
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": os.environ.get('OLLAMA_MODEL'), "prompt": user_msg},
                    stream=True,
                    timeout=30
                )
                response.raise_for_status()
                ai_reply = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode("utf-8"))
                        ai_reply += data.get("response", "")

            elif selected_model == "openrouter":
                print("🔁 Using OpenRouter...")
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": OPENROUTER_MODEL,
                    "messages": [
                        {"role": "user", "content": user_msg}
                    ]
                }
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                ai_reply = result["choices"][0]["message"]["content"]

            elif selected_model == "groq":
                print("🔁 Using Groq SDK...")
                groq_response = groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": user_msg}]
                )
                ai_reply = groq_response.choices[0].message.content

            else:
                print("🔁 Using Gemini...")
                response = gemini_model.generate_content(user_msg)
                ai_reply = getattr(response, "text", "No response from Gemini.")

            # Save AI reply
            ChatMessage.objects.create(sender="ai", message=ai_reply)

            return Response({"reply": ai_reply})

        except Exception as e:
            print("🔥 Exception occurred:", str(e))
            return Response({"error": str(e)}, status=500)
