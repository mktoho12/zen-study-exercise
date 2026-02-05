"""Data models for ZEN Study scraper."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Choice:
    """A choice in a question."""

    number: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"number": self.number, "text": self.text}


@dataclass
class Question:
    """A question in an exercise."""

    statement: str
    choices: list[Choice] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "statement": self.statement,
            "choices": [choice.to_dict() for choice in self.choices],
        }


@dataclass
class Exercise:
    """An exercise (confirmation test)."""

    exercise_id: int
    exercise_title: str
    questions: list[Question] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "exercise_id": self.exercise_id,
            "exercise_title": self.exercise_title,
            "questions": [question.to_dict() for question in self.questions],
        }


@dataclass
class Chapter:
    """A chapter in a course."""

    chapter_id: int
    chapter_title: str
    exercises: list[Exercise] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chapter_id": self.chapter_id,
            "chapter_title": self.chapter_title,
            "exercises": [exercise.to_dict() for exercise in self.exercises],
        }


@dataclass
class Course:
    """A course."""

    course_id: int
    course_title: str
    chapters: list[Chapter] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "course_id": self.course_id,
            "course_title": self.course_title,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
        }


@dataclass
class ExerciseCollection:
    """Collection of all courses with exercises."""

    courses: list[Course] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"courses": [course.to_dict() for course in self.courses]}
