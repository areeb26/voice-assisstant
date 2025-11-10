#!/usr/bin/env python3
"""
Jarvis - Voice-Activated AI Assistant
Run this to start voice-controlled assistant with wake word detection
"""
import asyncio
import logging
import time
from voice_handler import SpeechRecognizer, TextToSpeech, WakeWordDetector, BackgroundListener
from modules.nlp_processor import BilingualNLPProcessor
from services.gemini_service import GeminiService
from core.config import settings
from core.database import SessionLocal
from services.task_manager import TaskManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JarvisAssistant:
    """Jarvis - Your Personal AI Assistant"""

    def __init__(self):
        """Initialize Jarvis"""
        self.nlp = BilingualNLPProcessor()
        self.gemini = GeminiService()
        self.tts = TextToSpeech(language="en")

        logger.info("🤖 Jarvis AI Assistant Initialized")

        # Greet user
        if settings.VOICE_RESPONSE_ENABLED:
            self.tts.speak("Jarvis online. Ready to assist you, sir.")

    async def process_command(self, command: str, language: str = "en") -> str:
        """
        Process voice command using NLP and Gemini AI

        Args:
            command: Voice command text
            language: Language code

        Returns:
            Response text
        """
        logger.info(f"Processing command: {command}")

        # First try local NLP
        nlp_result = self.nlp.process(command, language)

        # Enhance with Gemini AI if available
        nlp_result = self.gemini.enhance_nlp_result(
            nlp_result,
            command,
            language
        )

        intent = nlp_result.get("intent", "unknown")

        # Handle different intents
        if intent == "create_task":
            return await self._handle_task_creation(nlp_result)
        elif intent == "list_tasks":
            return await self._handle_list_tasks()
        elif intent == "unknown":
            # Use Gemini for general chat
            response = self.gemini.chat(command, language)
            if response.get("success"):
                return response.get("response", "I'm not sure how to help with that.")
            else:
                return "I'm not sure how to help with that, sir."
        else:
            return self.gemini.generate_response(intent, language)

    async def _handle_task_creation(self, nlp_result: dict) -> str:
        """Handle task creation"""
        try:
            db = SessionLocal()
            task_manager = TaskManager(db)

            extracted_data = nlp_result.get("extracted_data", "")
            entities = nlp_result.get("entities", {})

            # Create task
            from schemas.task import TaskCreate
            task_data = TaskCreate(
                title=extracted_data,
                description=nlp_result.get("original_text", ""),
                language="en",
                priority=entities.get("priority", "medium")
            )

            task = task_manager.create_task(task_data)
            db.close()

            return f"Task created successfully, sir. Task: {task.title}"
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return "I encountered an error creating that task, sir."

    async def _handle_list_tasks(self) -> str:
        """Handle listing tasks"""
        try:
            db = SessionLocal()
            task_manager = TaskManager(db)

            tasks = task_manager.get_all_tasks()
            db.close()

            if not tasks:
                return "You have no tasks, sir."

            task_list = ", ".join([f"{t.title}" for t in tasks[:5]])
            return f"You have {len(tasks)} tasks, sir. Here are the top ones: {task_list}"
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return "I encountered an error retrieving your tasks, sir."

    def voice_command_handler(self, command: str, language: str) -> str:
        """
        Handler for background listener voice commands

        Args:
            command: Voice command
            language: Language code

        Returns:
            Response text
        """
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.process_command(command, language))
        loop.close()

        return response

    def start_listening(self):
        """Start background voice listener"""
        logger.info("🎤 Starting Jarvis voice listener...")

        # Create background listener
        listener = BackgroundListener(
            command_callback=self.voice_command_handler,
            language="en",
            wake_word_required=settings.VOICE_WAKE_WORD_REQUIRED
        )

        # Add custom wake words
        for wake_word in settings.VOICE_WAKE_WORDS:
            listener.wake_word_detector.add_wake_word(wake_word.strip())

        # Start listening
        listener.start()

        print("\n" + "="*60)
        print("🤖 JARVIS AI ASSISTANT - VOICE MODE ACTIVE")
        print("="*60)
        print("\nSay one of these wake words to activate:")
        for word in settings.VOICE_WAKE_WORDS:
            print(f"  - {word}")
        print("\nThen give your command!")
        print("\nExamples:")
        print("  - 'Jarvis, create a task to buy groceries'")
        print("  - 'Hey Jarvis, what's the weather today?'")
        print("  - 'Jarvis, list my tasks'")
        print("\nPress Ctrl+C to stop")
        print("="*60 + "\n")

        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n👋 Stopping Jarvis...")
            listener.stop()
            if settings.VOICE_RESPONSE_ENABLED:
                self.tts.speak("Goodbye, sir.")


def main():
    """Main entry point"""
    import time

    # Check if voice is enabled
    if not settings.VOICE_ENABLED:
        print("❌ Voice features are disabled in settings.")
        print("Enable VOICE_ENABLED=True in your .env file")
        return

    # Initialize Jarvis
    jarvis = JarvisAssistant()

    # Start voice listening
    jarvis.start_listening()


if __name__ == "__main__":
    main()
