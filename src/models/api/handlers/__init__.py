from langdetect import LangDetectException, detect  # type: ignore
from pydantic import BaseModel


class BaseHandler(BaseModel):
    detected_language: str = ""
    detected_language_error: bool = False
    detected_language_error_details: str = ""
    text: str = ""

    def __detect_language__(self):
        from src import app

        # langdetect does not work reliably for text with less than 200 characters
        if not self.text:
            message = "No text, skipping language detection"
            self.detected_language_error = True
            self.detected_language_error_details = message
            app.logger.error(message)
        else:
            if len(self.text) < 200:
                message = "Not enough text for us to reliably detect the language"
                self.detected_language_error = True
                self.detected_language_error_details = message
                app.logger.error(message)
            else:
                try:
                    self.detected_language = detect(self.text)
                    print(f"The detected language is: {self.detected_language}")
                except LangDetectException as e:
                    message = f"An error occurred while detecting the language: {e}"
                    self.detected_language_error = True
                    self.detected_language_error_details = message
                    app.logger.error(message)
