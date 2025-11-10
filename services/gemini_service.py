"""
Google Gemini AI Integration Service
Provides AI-powered natural language understanding and response generation
"""
import google.generativeai as genai
from typing import Dict, Any, Optional
import json
from ..core.config import settings


class GeminiService:
    """Service for interacting with Google Gemini API"""

    def __init__(self):
        """Initialize Gemini AI service"""
        if settings.USE_GEMINI_AI and settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            self.enabled = True
        else:
            self.enabled = False

    def analyze_intent(self, message: str, language: str = "en") -> Dict[str, Any]:
        """
        Analyze user message to extract intent and entities using Gemini AI

        Args:
            message: User's natural language message
            language: Language code (en or ur)

        Returns:
            Dictionary with intent, entities, and confidence
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Gemini AI is not enabled or configured"
            }

        try:
            lang_name = "English" if language == "en" else "Urdu"

            prompt = f"""You are an AI assistant that analyzes user commands in {lang_name}.
Analyze the following message and extract:
1. Intent (one of: create_task, list_tasks, complete_task, file_create, file_read, file_edit, execute_command, trigger_n8n, send_email, send_whatsapp, schedule_whatsapp, search, unknown)
2. Entities (like priority, due_date, file_path, etc.)
3. Confidence score (0.0 to 1.0)
4. A brief explanation

User message: "{message}"

Respond in JSON format:
{{
    "intent": "intent_name",
    "confidence": 0.95,
    "entities": {{}},
    "explanation": "brief explanation",
    "extracted_data": "main data extracted from command"
}}"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))

            return {
                "success": True,
                "intent": result.get("intent", "unknown"),
                "confidence": result.get("confidence", 0.0),
                "entities": result.get("entities", {}),
                "extracted_data": result.get("extracted_data"),
                "explanation": result.get("explanation", "")
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Gemini AI analysis failed: {str(e)}"
            }

    def generate_response(
        self,
        intent: str,
        language: str,
        context: Optional[Dict[str, Any]] = None,
        action_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate natural language response using Gemini AI

        Args:
            intent: The detected intent
            language: Language code (en or ur)
            context: Additional context about the request
            action_result: Result of the action taken

        Returns:
            Natural language response string
        """
        if not self.enabled:
            # Fallback to simple responses
            return self._get_fallback_response(intent, language)

        try:
            lang_name = "English" if language == "en" else "Urdu"

            prompt = f"""You are a helpful AI assistant. Generate a brief, friendly response in {lang_name}.

Intent: {intent}
Context: {json.dumps(context or {})}
Action Result: {json.dumps(action_result or {})}

Generate a natural, concise response (1-2 sentences) that:
1. Confirms the action was taken (or explain if it failed)
2. Is friendly and helpful
3. Is in {lang_name} language only

Response:"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            return self._get_fallback_response(intent, language)

    def enhance_nlp_result(
        self,
        local_result: Dict[str, Any],
        message: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Enhance local NLP results with Gemini AI analysis

        Args:
            local_result: Result from local pattern-based NLP
            message: Original user message
            language: Language code

        Returns:
            Enhanced NLP result
        """
        if not self.enabled:
            return local_result

        try:
            # If local NLP has low confidence or unknown intent, use Gemini
            if local_result.get("confidence", 0) < 0.7 or local_result.get("intent") == "unknown":
                gemini_result = self.analyze_intent(message, language)

                if gemini_result.get("success"):
                    return {
                        "intent": gemini_result.get("intent", local_result.get("intent")),
                        "confidence": gemini_result.get("confidence", local_result.get("confidence")),
                        "entities": {
                            **local_result.get("entities", {}),
                            **gemini_result.get("entities", {})
                        },
                        "extracted_data": gemini_result.get("extracted_data") or local_result.get("extracted_data"),
                        "language": language,
                        "detected_language": local_result.get("detected_language", language),
                        "original_text": message,
                        "enhanced_by_ai": True,
                        "explanation": gemini_result.get("explanation", "")
                    }

            return local_result

        except Exception as e:
            # If Gemini fails, return original result
            return local_result

    def _get_fallback_response(self, intent: str, language: str) -> str:
        """Fallback responses when Gemini is not available"""
        responses = {
            "en": {
                "create_task": "Task created successfully!",
                "list_tasks": "Here are your tasks:",
                "complete_task": "Task marked as completed!",
                "file_create": "File created successfully!",
                "file_read": "Here's the file content:",
                "file_edit": "File updated successfully!",
                "execute_command": "Command executed successfully!",
                "trigger_n8n": "Workflow triggered successfully!",
                "send_email": "Email sent successfully!",
                "send_whatsapp": "WhatsApp message sent successfully!",
                "schedule_whatsapp": "WhatsApp message scheduled successfully!",
                "search": "Here are the search results:",
                "unknown": "I'm not sure what you want me to do. Can you please rephrase?",
            },
            "ur": {
                "create_task": "کام کامیابی سے بنایا گیا!",
                "list_tasks": "یہ آپ کے کام ہیں:",
                "complete_task": "کام مکمل کر دیا گیا!",
                "file_create": "فائل کامیابی سے بنائی گئی!",
                "file_read": "فائل کا مواد:",
                "file_edit": "فائل اپ ڈیٹ ہو گئی!",
                "execute_command": "کمانڈ چل گئی!",
                "trigger_n8n": "ورک فلو شروع ہو گیا!",
                "send_email": "ای میل بھیج دی گئی!",
                "send_whatsapp": "واٹس ایپ پیغام بھیج دیا گیا!",
                "schedule_whatsapp": "واٹس ایپ پیغام شیڈول ہو گیا!",
                "search": "تلاش کے نتائج:",
                "unknown": "مجھے سمجھ نہیں آیا۔ برائے مہربانی دوبارہ بتائیں؟",
            },
        }

        return responses.get(language, responses["en"]).get(intent, responses[language].get("unknown", ""))

    def chat(self, message: str, language: str = "en", history: Optional[list] = None) -> Dict[str, Any]:
        """
        General chat interface with Gemini AI

        Args:
            message: User's message
            language: Language code (en or ur)
            history: Conversation history (optional)

        Returns:
            Dictionary with response and metadata
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Gemini AI is not enabled or configured"
            }

        try:
            lang_name = "English" if language == "en" else "Urdu"

            chat_prompt = f"""You are a helpful bilingual AI assistant that can understand and respond in both {lang_name}.
Be concise, friendly, and helpful. Respond in the same language as the user's message.

User: {message}
Assistant:"""

            response = self.model.generate_content(chat_prompt)

            return {
                "success": True,
                "response": response.text.strip(),
                "language": language
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Gemini AI chat failed: {str(e)}"
            }
