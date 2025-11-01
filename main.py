import random
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import statistics


class PuzzleGenerator:
    """Generates math puzzles based on difficulty level."""
    
    DIFFICULTY_CONFIG = {
        'Easy': {
            'num_range': (1, 10),
            'operators': ['+', '-'],
            'time_limit': 30
        },
        'Medium': {
            'num_range': (5, 20),
            'operators': ['+', '-', '*'],
            'time_limit': 20
        },
        'Hard': {
            'num_range': (10, 50),
            'operators': ['+', '-', '*', '/'],
            'time_limit': 15
        }
    }
    
    @staticmethod
    def generate(difficulty: str) -> Dict:
        """Generate a single puzzle."""
        config = PuzzleGenerator.DIFFICULTY_CONFIG[difficulty]
        num_range = config['num_range']
        
        num1 = random.randint(num_range[0], num_range[1])
        num2 = random.randint(num_range[0], num_range[1])
        operator = random.choice(config['operators'])
        
        # Calculate answer
        if operator == '+':
            answer = num1 + num2
        elif operator == '-':
            answer = num1 - num2
        elif operator == '*':
            answer = num1 * num2
        else:  # division
            answer = num1 // num2
        
        return {
            'num1': num1,
            'num2': num2,
            'operator': operator,
            'answer': answer,
            'difficulty': difficulty,
            'time_limit': config['time_limit']
        }



class PerformanceTracker:
    """Tracks user performance metrics."""
    
    def __init__(self):
        self.attempts = []
    
    def log_attempt(self, puzzle: Dict, user_answer: int, time_taken: float, correct: bool):
        """Log a single attempt."""
        attempt = {
            'puzzle': f"{puzzle['num1']} {puzzle['operator']} {puzzle['num2']}",
            'correct_answer': puzzle['answer'],
            'user_answer': user_answer,
            'time_taken': time_taken,
            'correct': correct,
            'difficulty': puzzle['difficulty'],
            'timestamp': datetime.now().isoformat()
        }
        self.attempts.append(attempt)
    
    def get_stats(self) -> Dict:
        """Calculate session statistics."""
        if not self.attempts:
            return {}
        
        correct_count = sum(1 for a in self.attempts if a['correct'])
        incorrect_count = len(self.attempts) - correct_count
        times = [a['time_taken'] for a in self.attempts]
        
        return {
            'total_attempts': len(self.attempts),
            'correct': correct_count,
            'incorrect': incorrect_count,
            'accuracy': (correct_count / len(self.attempts)) * 100,
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'difficulty_progression': [a['difficulty'] for a in self.attempts]
        }
    
    def get_recent_performance(self, n: int = 5) -> float:
        """Get accuracy of last n attempts (0-1)."""
        recent = self.attempts[-n:]
        if not recent:
            return 0.5
        correct = sum(1 for a in recent if a['correct'])
        return correct / len(recent)


class AdaptiveEngine:
    """Rule-based adaptive learning logic."""
    
    DIFFICULTY_LEVELS = ['Easy', 'Medium', 'Hard']
    
    @staticmethod
    def calculate_next_difficulty(
        current_difficulty: str,
        correct: bool,
        time_taken: float,
        time_limit: float,
        tracker: PerformanceTracker
    ) -> str:
        """
        Adaptive logic: Adjust difficulty based on performance.
        
        SCORING SYSTEM (0-100 points):
        - +40 points if answer is CORRECT
        - +30 points if time < 70% of time limit (quick answer)
        - +30 points if recent accuracy (last 5) > 70% (consistent performance)
        
        DECISION RULES:
        - Score >= 90 → INCREASE difficulty (learner ready for harder)
        - Score < 40  → DECREASE difficulty (learner struggling)
        - Otherwise   → MAINTAIN current difficulty
        """
        
        current_idx = AdaptiveEngine.DIFFICULTY_LEVELS.index(current_difficulty)
        recent_accuracy = tracker.get_recent_performance(n=5)
        time_efficiency = time_taken / time_limit
        
        # Calculate score (0-100)
        score = 0
        
        # 1. Check if answer is correct
        if correct:
            score += 40
        
        # 2. Check if solved quickly (less than 70% of time limit)
        if time_efficiency < 0.7:
            score += 30
        
        # 3. Check if recent performance is good (last 5 attempts)
        if recent_accuracy > 0.7:
            score += 30
        
        # Make adaptive decision based on score
        if score >= 90 and current_idx < 2:
            # Increase difficulty (move to harder level)
            return AdaptiveEngine.DIFFICULTY_LEVELS[current_idx + 1]
        elif score < 40 and current_idx > 0:
            # Decrease difficulty (move to easier level)
            return AdaptiveEngine.DIFFICULTY_LEVELS[current_idx - 1]
        else:
            # Stay at current difficulty
            return current_difficulty



class AdaptiveSession:
    """Main session controller - orchestrates the learning experience."""
    
    def __init__(self, player_name: str, initial_difficulty: str = 'Medium'):
        self.player_name = player_name
        self.current_difficulty = initial_difficulty
        self.tracker = PerformanceTracker()
        self.puzzle_count = 0
        self.max_puzzles = 10
    
    def run_puzzle(self):
        """Run a single puzzle interaction."""
        puzzle = PuzzleGenerator.generate(self.current_difficulty)
        
        # Display puzzle
        print(f"\n{'='*60}")
        print(f"PUZZLE {self.puzzle_count + 1}/{self.max_puzzles}")
        print(f"{'='*60}")
        print(f"Current Difficulty: {self.current_difficulty}")
        print(f"Time Limit: {puzzle['time_limit']} seconds")
        print(f"{'='*60}")
        print(f"\n{puzzle['num1']} {puzzle['operator']} {puzzle['num2']} = ?\n")
        
        start_time = time.time()
        
        # Get user answer
        try:
            user_answer = int(input("Your answer: "))
        except ValueError:
            user_answer = -1
        
        time_taken = time.time() - start_time
        correct = user_answer == puzzle['answer']
        
        # Display feedback
        print()
        if correct:
            print(f"✓ CORRECT! Time taken: {time_taken:.2f}s")
        else:
            print(f"✗ WRONG - Correct answer was: {puzzle['answer']}")
        
        # Track this attempt
        self.tracker.log_attempt(puzzle, user_answer, time_taken, correct)
        
        # Calculate next difficulty
        old_difficulty = self.current_difficulty
        self.current_difficulty = AdaptiveEngine.calculate_next_difficulty(
            self.current_difficulty,
            correct,
            time_taken,
            puzzle['time_limit'],
            self.tracker
        )
        
        # Show difficulty change if it happened
        if old_difficulty != self.current_difficulty:
            print(f"\n📊 Difficulty adjusted: {old_difficulty} → {self.current_difficulty}")
        else:
            print(f"\n📊 Difficulty stays: {self.current_difficulty}")
        
        self.puzzle_count += 1
    
    def display_summary(self):
        """Display session summary."""
        stats = self.tracker.get_stats()
        
        print(f"\n\n{'='*60}")
        print(f"SESSION COMPLETE - {self.player_name.upper()}")
        print(f"{'='*60}")
        print(f"Total Puzzles: {stats['total_attempts']}")
        print(f"Correct Answers: {stats['correct']}")
        print(f"Wrong Answers: {stats['incorrect']}")
        print(f"Accuracy: {stats['accuracy']:.1f}%")
        print(f"Average Time per Puzzle: {stats['avg_time']:.2f}s")
        print(f"Fastest Answer: {stats['min_time']:.2f}s")
        print(f"Slowest Answer: {stats['max_time']:.2f}s")
        print(f"Final Difficulty Level: {self.current_difficulty}")
        print(f"\nDifficulty Progression:")
        print(f"{' → '.join(stats['difficulty_progression'])}")
        print(f"{'='*60}\n")
        
        return stats
    
    def save_session(self, filename: str = None):
        """Save session data to JSON file."""
        if not filename:
            # Create sessions directory if it doesn't exist
            if not os.path.exists('sessions'):
                os.makedirs('sessions')
            
            filename = f"sessions/session_{self.player_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'player': self.player_name,
            'initial_difficulty': 'Medium',  # Default
            'final_difficulty': self.current_difficulty,
            'timestamp': datetime.now().isoformat(),
            'attempts': self.tracker.attempts,
            'stats': self.tracker.get_stats()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Session data saved to: {filename}")



def main():
    """Main entry point - runs the complete adaptive learning system."""
    
    print("\n" + "="*60)
    print("      ADAPTIVE MATH LEARNING SYSTEM")
    print("      AI-Powered Personalized Learning")
    print("="*60)
    
    # Step 1: Get player name
    print("\nWelcome! Let's start learning math with adaptive difficulty.")
    player_name = input("\nEnter your name: ").strip()
    
    if not player_name:
        player_name = "Learner"
    
    # Step 2: Choose initial difficulty
    print(f"\nHello, {player_name}! Choose your starting difficulty level:\n")
    print("1. EASY (Numbers 1-10, Operations: + and -)")
    print("2. MEDIUM (Numbers 5-20, Operations: +, -, and *)")
    print("3. HARD (Numbers 10-50, Operations: +, -, *, and ÷)")
    
    difficulty_map = {'1': 'Easy', '2': 'Medium', '3': 'Hard'}
    
    while True:
        choice = input("\nEnter your choice (1, 2, or 3): ").strip()
        if choice in difficulty_map:
            initial_difficulty = difficulty_map[choice]
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    print(f"\n✓ Starting at {initial_difficulty} level")
    
    # Step 3: Create and run session
    session = AdaptiveSession(player_name, initial_difficulty)
    
    print(f"\nYou will solve {session.max_puzzles} math puzzles.")
    print("The difficulty will adjust based on your performance!")
    input("\nPress Enter to start the first puzzle...")
    
    # Run all puzzles
    while session.puzzle_count < session.max_puzzles:
        session.run_puzzle()
        
        if session.puzzle_count < session.max_puzzles:
            input("\nPress Enter for the next puzzle...")
    
    # Step 4: Display summary
    stats = session.display_summary()
    
    # Step 5: Save session
    print("Would you like to save this session data?")
    save = input("Enter 'y' for yes or 'n' for no: ").strip().lower()
    
    if save == 'y':
        session.save_session()
    
    print(f"\nThanks for learning with us, {player_name}!")
    print("Keep practicing to improve your math skills!\n")
# run the main program

if __name__ == "__main__":
    main()