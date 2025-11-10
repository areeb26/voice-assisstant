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
    level=logging.DEBUG,  # Changed to DEBUG to see detailed logs
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
        try:
            logger.info(f"[JARVIS] Processing command: {command}")

            # First try local NLP
            logger.debug(f"[JARVIS] Running NLP processor...")
            nlp_result = self.nlp.process(command, language)
            logger.debug(f"[JARVIS] NLP result: intent={nlp_result.get('intent')}, confidence={nlp_result.get('confidence')}")

            # Enhance with Gemini AI if available
            logger.debug(f"[JARVIS] Enhancing with Gemini AI...")
            nlp_result = self.gemini.enhance_nlp_result(
                nlp_result,
                command,
                language
            )

            intent = nlp_result.get("intent", "unknown")
            logger.info(f"[JARVIS] Detected intent: {intent}")

            # Handle different intents
            if intent == "create_task":
                logger.debug(f"[JARVIS] Handling task creation...")
                return await self._handle_task_creation(nlp_result)
            elif intent == "list_tasks":
                logger.debug(f"[JARVIS] Handling list tasks...")
                return await self._handle_list_tasks()
            elif intent == "unknown":
                # Use Gemini for general chat
                logger.debug(f"[JARVIS] Using Gemini chat for unknown intent...")
                response = self.gemini.chat(command, language)
                logger.debug(f"[JARVIS] Gemini chat response: success={response.get('success')}")

                if response.get("success"):
                    response_text = response.get("response", "I'm not sure how to help with that.")
                    logger.info(f"[JARVIS] Returning Gemini response: {response_text[:50]}...")
                    return response_text
                else:
                    logger.warning(f"[JARVIS] Gemini chat failed: {response.get('error')}")
                    return "I'm not sure how to help with that, sir."
            else:
                logger.debug(f"[JARVIS] Generating response for intent: {intent}")
                response_text = self.gemini.generate_response(intent, language)
                logger.info(f"[JARVIS] Generated response: {response_text[:50]}...")
                return response_text

        except Exception as e:
            logger.error(f"[JARVIS] Error in process_command: {e}", exc_info=True)
            return f"Sorry sir, I encountered an error: {str(e)}"

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
        try:
            logger.info(f"[HANDLER] voice_command_handler called with command='{command}', language='{language}'")

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.debug(f"[HANDLER] Created new event loop, running process_command...")

            response = loop.run_until_complete(self.process_command(command, language))

            logger.debug(f"[HANDLER] process_command completed")
            loop.close()

            logger.info(f"[HANDLER] Generated response for command '{command}': {response}")
            return response

        except Exception as e:
            logger.error(f"[HANDLER] Error in voice_command_handler: {e}", exc_info=True)
            return f"Error processing command: {str(e)}"

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
