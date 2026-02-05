"""Generate markdown files from output JSON files."""

import json
from pathlib import Path


def generate_markdown_for_course(course_dir: Path) -> None:
    """Generate markdown file for a course.
    
    Args:
        course_dir: Path to course directory
    """
    course_name = course_dir.name.rsplit('_', 1)[0]  # Remove course_id from name
    
    # Collect all questions
    questions_by_chapter = {}
    
    for chapter_dir in sorted(course_dir.iterdir()):
        if not chapter_dir.is_dir():
            continue
            
        chapter_name = chapter_dir.name
        questions = []

        # Sort by filename to maintain API response order (files are prefixed with index)
        for json_file in sorted(chapter_dir.glob("*.json")):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                questions.append(data)
        
        if questions:
            questions_by_chapter[chapter_name] = questions
    
    # Generate markdown
    md_lines = []
    md_lines.append(f"# {course_name}\n")
    
    for chapter_name, questions in questions_by_chapter.items():
        chapter_title = chapter_name.rsplit('_', 1)[0]  # Remove chapter_id
        md_lines.append(f"## {chapter_title}\n")
        
        for q_data in questions:
            exercise_title = q_data['exercise_title']
            question = q_data['question']
            q_num = q_data['question_number']
            
            md_lines.append(f"### {exercise_title} - 問{q_num}\n")
            md_lines.append(f"**問題:** {question['statement']}\n")
            
            for choice in question['choices']:
                md_lines.append(f"{choice['number']}. {choice['text']}")
            
            md_lines.append("\n---\n")
    
    # Save markdown file
    output_file = Path("output") / f"{course_name}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"✓ 生成: {output_file.name}")


def main():
    """Main entry point."""
    print("マークダウン生成ツール")
    print("=" * 50)
    
    output_dir = Path("output")
    
    if not output_dir.exists():
        print("エラー: output ディレクトリが見つかりません")
        return
    
    # Process each course directory
    for course_dir in sorted(output_dir.iterdir()):
        if course_dir.is_dir():
            generate_markdown_for_course(course_dir)
    
    print("\n完了！")


if __name__ == "__main__":
    main()
