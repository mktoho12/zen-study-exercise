"""Main entry point for ZEN Study exercise scraper."""

import json
import os
import re
from pathlib import Path

from .client import ZenStudyClient
from .config import Config
from .models import Chapter, Course, Exercise, ExerciseCollection, Question
from .parser import ExerciseParser


def sanitize_filename(name: str) -> str:
    """Sanitize string for use as filename.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string safe for filename
    """
    # Remove or replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces and other problematic chars
    name = name.replace(' ', '_')
    # Limit length
    if len(name) > 100:
        name = name[:100]
    return name


def save_question_file(
    course_title: str,
    course_id: int,
    chapter_title: str,
    chapter_id: int,
    exercise_title: str,
    exercise_id: int,
    exercise_index: int,
    question_num: int,
    question: Question,
) -> Path:
    """Save a single question to a JSON file.

    Args:
        course_title: Course title
        course_id: Course ID
        chapter_title: Chapter title
        chapter_id: Chapter ID
        exercise_title: Exercise title
        exercise_id: Exercise ID
        exercise_index: Exercise index in chapter (0-indexed)
        question_num: Question number (1-indexed)
        question: Question object

    Returns:
        Path to saved file
    """
    # Create directory structure
    output_base = Path(Config.OUTPUT_DIR)

    course_dir = sanitize_filename(f"{course_title}_{course_id}")
    chapter_dir = sanitize_filename(f"{chapter_title}_{chapter_id}")

    dir_path = output_base / course_dir / chapter_dir
    dir_path.mkdir(parents=True, exist_ok=True)

    # Create filename with exercise index for proper ordering
    exercise_safe = sanitize_filename(exercise_title)
    filename = f"{exercise_index:03d}_{exercise_safe}_{exercise_id}_q{question_num}.json"
    file_path = dir_path / filename

    # Save question data
    question_data = {
        "course_id": course_id,
        "course_title": course_title,
        "chapter_id": chapter_id,
        "chapter_title": chapter_title,
        "exercise_id": exercise_id,
        "exercise_title": exercise_title,
        "exercise_index": exercise_index,
        "question_number": question_num,
        "question": question.to_dict(),
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(question_data, f, ensure_ascii=False, indent=2)

    return file_path


def normalize_exercise_url(content_url: str) -> str:
    """Remove /result from exercise URL if present.

    Args:
        content_url: Original content URL

    Returns:
        Normalized URL without /result
    """
    return content_url.replace("/result", "")


def is_ondemand_course(course_title: str) -> bool:
    """Check if course is an on-demand course.

    Args:
        course_title: Course title

    Returns:
        True if the course is on-demand (contains 'オンデマンド')
    """
    return "オンデマンド" in course_title


def scrape_exercises() -> ExerciseCollection:
    """Scrape exercises from ZEN Study.

    Returns:
        ExerciseCollection containing all courses and exercises
    """
    collection = ExerciseCollection()

    with ZenStudyClient() as client:
        print("コース一覧を取得中...")
        my_courses_response = client.get_my_courses()

        # Extract courses from services array
        courses_data = []
        for service in my_courses_response.get("services", []):
            courses_data.extend(service.get("courses", []))

        ondemand_courses = [
            c for c in courses_data if is_ondemand_course(c.get("title", ""))
        ]

        print(f"オンデマンドコース {len(ondemand_courses)} 件を発見\n")

        for course_data in ondemand_courses:
            course_id = course_data.get("id")
            course_title = course_data.get("title", "")

            print(f"【{course_title}】")

            course = Course(course_id=course_id, course_title=course_title)

            # Get course info (chapters)
            course_info = client.get_course_info(course_id)
            chapters_data = course_info.get("course", {}).get("chapters", [])

            for chapter_data in chapters_data:
                chapter_id = chapter_data.get("id")
                chapter_title = chapter_data.get("title", "")

                print(f"  > {chapter_title}")

                chapter = Chapter(chapter_id=chapter_id, chapter_title=chapter_title)

                # Get chapter info (sections)
                chapter_info = client.get_chapter_info(course_id, chapter_id)
                sections = chapter_info.get("chapter", {}).get("sections", [])

                # Filter exercises only
                exercises_data = [
                    s for s in sections if s.get("resource_type") == "exercise"
                ]

                for idx, exercise_data in enumerate(exercises_data, 1):
                    exercise_id = exercise_data.get("id")
                    exercise_title = exercise_data.get("title", "")
                    content_url = exercise_data.get("content_url", "")

                    total_exercises = len(exercises_data)
                    print(
                        f"    - 確認テスト {idx}/{total_exercises}: {exercise_title}"
                    )

                    # Normalize URL (remove /result)
                    exercise_url = normalize_exercise_url(content_url)

                    try:
                        # Get exercise HTML
                        html = client.get_exercise_html(exercise_url)

                        # Parse questions
                        questions = ExerciseParser.parse_exercise_html(html)

                        if questions:
                            # Save each question immediately
                            for q_num, question in enumerate(questions, 1):
                                file_path = save_question_file(
                                    course_title=course_title,
                                    course_id=course_id,
                                    chapter_title=chapter_title,
                                    chapter_id=chapter_id,
                                    exercise_title=exercise_title,
                                    exercise_id=exercise_id,
                                    exercise_index=idx,  # Use 1-indexed value
                                    question_num=q_num,
                                    question=question,
                                )
                                print(f"      ✓ 問{q_num} 保存: {file_path.name}")

                            # Still keep in memory for final summary
                            exercise = Exercise(
                                exercise_id=exercise_id,
                                exercise_title=exercise_title,
                                questions=questions,
                            )
                            chapter.exercises.append(exercise)
                        else:
                            print("      ! 問題が見つかりませんでした")

                    except Exception as e:
                        print(f"      ! エラー: {e}")

                if chapter.exercises:
                    course.chapters.append(chapter)

            if course.chapters:
                collection.courses.append(course)

            print()

    return collection


def save_summary(collection: ExerciseCollection) -> None:
    """Save summary JSON file with all courses and exercises.

    Args:
        collection: ExerciseCollection to save
    """
    output_dir = Path(Config.OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    summary_path = output_dir / "summary.json"

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(collection.to_dict(), f, ensure_ascii=False, indent=2)

    print(f"\nサマリーを {summary_path} に保存しました")


def main():
    """Main entry point."""
    print("ZEN Study 確認テスト取得ツール")
    print("=" * 50)
    print()

    try:
        collection = scrape_exercises()

        if not collection.courses:
            print("取得できた確認テストがありませんでした。")
            return

        save_summary(collection)

        # Print summary
        total_courses = len(collection.courses)
        total_chapters = sum(len(c.chapters) for c in collection.courses)
        total_exercises = sum(
            len(ch.exercises) for c in collection.courses for ch in c.chapters
        )
        total_questions = sum(
            len(ex.questions)
            for c in collection.courses
            for ch in c.chapters
            for ex in ch.exercises
        )

        print()
        print("=" * 50)
        print("取得完了:")
        print(f"  コース: {total_courses} 件")
        print(f"  チャプター: {total_chapters} 件")
        print(f"  確認テスト: {total_exercises} 件")
        print(f"  問題数: {total_questions} 問")

    except KeyboardInterrupt:
        print("\n\n中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        raise


if __name__ == "__main__":
    main()
