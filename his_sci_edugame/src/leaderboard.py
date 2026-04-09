"""
Leaderboard Management
Stores and retrieves player scores
"""

import json
import os
from typing import List, Dict
from datetime import datetime


class Leaderboard:
    def __init__(self, filename: str = 'leaderboard.json'):
        """
        Initialize the leaderboard.

        Args:
            filename: JSON file to store leaderboard data
        """
        self.filename = filename
        self.scores = []
        self.load_scores()

    def load_scores(self):
        """Load scores from JSON file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.scores = []
        else:
            self.scores = []

    def save_scores(self):
        """Save scores to JSON file"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving leaderboard: {e}")

    def add_score(self, name: str, score: int, questions_answered: int, topic: str = None):
        """
        Add a new score to the leaderboard.

        Args:
            name: Player name
            score: Final score
            questions_answered: Number of questions answered
            topic: Optional topic name
        """
        entry = {
            'name': name,
            'score': score,
            'questions_answered': questions_answered,
            'topic': topic or 'Random',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.scores.append(entry)

        def _sort_key(x):
            if x.get('topic') == 'Speedrun':
                return (0, x['score'])
            else:
                return (1, -x['score'])

        self.scores.sort(key=_sort_key)
        self.scores = self.scores[:100]
        self.save_scores()

    def get_top_scores(self, limit: int = 10) -> List[Dict]:
        """
        Get top N scores.

        Args:
            limit: Number of top scores to return

        Returns:
            List of score dictionaries
        """
        return self.scores[:limit]

    def get_player_best(self, name: str) -> Dict:
        """
        Get the best score for a specific player.

        Args:
            name: Player name

        Returns:
            Best score dictionary or None
        """
        player_scores = [s for s in self.scores if s['name'].lower() == name.lower()]
        if player_scores:
            return max(player_scores, key=lambda x: x['score'])
        return None
