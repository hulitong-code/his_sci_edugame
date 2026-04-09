"""
Science Questions Database
Reads questions from text files in the questions/ directory
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import random
import os

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

@dataclass
class Question:
    question: str
    answers: List[str]
    correct_answer: str
    topic: str
    difficulty: Difficulty
    explanation: Optional[str] = None
    image_path: Optional[str] = None

class ScienceQuestions:
    def __init__(self, questions_dir: str = "questions"):
        """
        Initialize the questions database.

        Args:
            questions_dir: Directory containing question text files
        """
        self.questions_dir = questions_dir
        self.questions = []
        self._load_questions_from_files()

    def _parse_question_file(self, filepath: str, topic: str) -> List[Question]:
        """
        Parse a question file and return a list of Question objects.

        Format:
        Question text
        a. Option A (correct answer)
        b. Option B
        c. Option C
        d. Option D
        Explanation: Optional explanation text
        (blank line between questions)
        """
        questions = []

        if not os.path.exists(filepath):
            print(f"Warning: Question file not found: {filepath}")
            return questions

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into blocks separated by blank lines
        question_blocks = []
        current_block = []

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                if current_block:
                    question_blocks.append("\n".join(current_block))
                    current_block = []
            else:
                current_block.append(line)

        # Don't forget the last block
        if current_block:
            question_blocks.append("\n".join(current_block))

        # Parse each block into a Question
        for block in question_blocks:
            if not block.strip():
                continue

            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if len(lines) < 5:
                continue

            question_text = lines[0]
            options = {}
            explanation = None
            image_path = None

            # Parse options (lines 1-4)
            for i in range(1, min(5, len(lines))):
                line = lines[i]
                if line.startswith("a.") or line.startswith("a "):
                    options["a"] = line[2:].strip()
                elif line.startswith("b.") or line.startswith("b "):
                    options["b"] = line[2:].strip()
                elif line.startswith("c.") or line.startswith("c "):
                    options["c"] = line[2:].strip()
                elif line.startswith("d.") or line.startswith("d "):
                    options["d"] = line[2:].strip()

            # Parse extra fields (explanation, image)
            for line in lines[5:]:
                if line.lower().startswith("explanation:"):
                    explanation = line[12:].strip()
                elif line.lower().startswith("image:"):
                    image_path = line[6:].strip()

                    if image_path and not os.path.isabs(image_path):
                        questions_dir = os.path.dirname(filepath)
                        image_path = os.path.join(questions_dir, "images", image_path)

            # Only create question if we have all 4 options
            if len(options) == 4 and "a" in options:
                # First option (a) is always the correct answer
                answers = [options["a"], options["b"], options["c"], options["d"]]
                correct_answer = options["a"]

                # Assign random difficulty
                rand = random.random()
                if rand < 0.6:
                    difficulty = Difficulty.EASY
                elif rand < 0.9:
                    difficulty = Difficulty.MEDIUM
                else:
                    difficulty = Difficulty.HARD

                question = Question(
                    question=question_text,
                    answers=answers,
                    correct_answer=correct_answer,
                    topic=topic,
                    difficulty=difficulty,
                    explanation=explanation,
                    image_path=image_path if image_path and os.path.exists(image_path) else None,
                )

                questions.append(question)

        return questions

    def _load_questions_from_files(self):
        """Load all questions from text files in the questions directory"""
        if not os.path.exists(self.questions_dir):
            print(f"Warning: Questions directory not found: {self.questions_dir}")
            return

        # Map topics to their filenames
        topic_files = {
            "water_cycle": "water_cycle.txt",
            "states_of_matter": "states_of_matter.txt",
            "solar_system": "solar_system.txt",
            "plants": "plants.txt",
            "animals": "animals.txt",
        }

        for topic, filename in topic_files.items():
            filepath = os.path.join(self.questions_dir, filename)
            questions = self._parse_question_file(filepath, topic)
            self.questions.extend(questions)
            print(f"Loaded {len(questions)} questions from {filename}")

        print(f"Total questions loaded: {len(self.questions)}")

    def reload_questions(self):
        """Reload questions from files (useful when files are modified)"""
        self.questions = []
        self._load_questions_from_files()

    def get_random_question(self, difficulty: Difficulty) -> Optional[Question]:
        """Get a random question of the specified difficulty"""
        available = [q for q in self.questions if q.difficulty == difficulty]
        if not available:
            # Fall back to any question
            available = self.questions
        if available:
            return random.choice(available)
        return None

    def get_question_by_topic(self, topic: str, difficulty: Difficulty) -> Optional[Question]:
        """Get a random question for a specific topic and difficulty"""
        available = [q for q in self.questions
                     if q.topic == topic and q.difficulty == difficulty]

        if not available:
            # Fall back to just topic matching
            available = [q for q in self.questions if q.topic == topic]

        if not available:
            # Fall back to any question with matching difficulty
            return self.get_random_question(difficulty)
        if available:
            return random.choice(available)
        return None

    def get_all_topics(self) -> List[str]:
        """Get a list of all available topics"""
        return list(set(q.topic for q in self.questions))
