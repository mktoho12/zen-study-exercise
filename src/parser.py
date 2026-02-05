"""HTML parser for ZEN Study exercise pages."""

import re

from bs4 import BeautifulSoup

from .models import Choice, Question


class ExerciseParser:
    """Parser for exercise HTML pages."""

    @staticmethod
    def parse_exercise_html(html: str) -> list[Question]:
        """Parse exercise HTML and extract questions and choices.

        Args:
            html: HTML content of exercise page

        Returns:
            List of Question objects
        """
        soup = BeautifulSoup(html, "html.parser")
        questions = []

        # Find the kokuban container
        kokuban = soup.find("div", id="kokuban-input-target")
        if not kokuban:
            # Some exercises might not have the kokuban container, try searching from root
            kokuban = soup

        # Find all exercise sections
        exercise_sections = kokuban.find_all("section", class_="exercise")

        for section in exercise_sections:
            # Extract question statement
            statement_div = section.find("div", class_="statement")
            if not statement_div:
                continue

            statement_text = statement_div.get_text(strip=True)
            if not statement_text:
                continue

            # Initialize choices
            choices = []
            question_found = False

            # Try to parse as a multiple-choice question
            answers_ul = section.find("ul", class_="answers")
            if answers_ul:
                choice_items = answers_ul.find_all("li", attrs={"data-input-value": True})
                if choice_items:
                    for item in choice_items:
                        choice_number_str = item.get("data-input-value", "")
                        try:
                            choice_number = int(choice_number_str)
                        except ValueError:
                            continue

                        choice_text = item.get_text(strip=True)
                        choice_text = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", choice_text)
                        choice_text = re.sub(r"^\d+\.\s*", "", choice_text)
                        choice_text = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]", "", choice_text)

                        if choice_text:
                            choices.append(Choice(number=choice_number, text=choice_text))
                    
                    if choices:
                        question_found = True

            # If not a multiple-choice, check for fill-in-the-blank (word input)
            if not question_found:
                word_input_li = section.find("li", attrs={"data-type": "word"})
                if word_input_li and word_input_li.find("input", class_="answers"):
                    # This is a fill-in-the-blank question.
                    # We record the question statement, but there are no choices to record.
                    question_found = True

            # If any type of question was found, create the Question object
            if question_found:
                question = Question(statement=statement_text, choices=choices)
                questions.append(question)

        return questions
