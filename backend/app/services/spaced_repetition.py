"""
Spaced Repetition Service — Implements the SuperMemo-2 (SM-2) algorithm.
"""

def calculate_sm2(
    is_correct: bool, 
    current_interval: int, 
    current_ease: float, 
    quality_modifier: float = 0.0
) -> tuple[int, float]:
    """
    Computes the new interval (in days) and new ease factor based on SM-2.

    Args:
        is_correct: Whether the user got the question right.
        current_interval: The number of days since the last review interval. 
                          Pass 0 if this is the first attempt.
        current_ease: The prior ease factor (typically starts at 2.5).
        quality_modifier: Optional value from -1.0 to 1.0 based on speed/confidence.
                          Positive = faster/more confident, Negative = slower/less confident.

    Returns:
        tuple[int, float]: (next_interval_days, new_ease_factor)
    """
    # 1. Determine quality score (0 to 5)
    # SM-2 quality:
    # 5 - perfect response
    # 4 - correct response after a hesitation
    # 3 - correct response recalled with serious difficulty
    # 2 - incorrect response; where the correct one seemed easy to recall
    # 1 - incorrect response; the correct one remembered
    # 0 - complete blackout
    
    if is_correct:
        base_quality = 4.0
    else:
        base_quality = 1.0
        
    quality = base_quality + quality_modifier
    quality = max(0.0, min(5.0, quality))

    # 2. Update ease factor
    # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    
    # SM-2 enforces a hard floor on ease factor to prevent infinite review loops
    # 1.3 is the standard floor.
    new_ease = max(1.3, min(10.0, new_ease))

    # 3. Compute next interval
    if not is_correct:
        # Incorrect resets the streak
        next_interval = 1
    else:
        # Correct answer
        if current_interval == 0:
            next_interval = 1
        elif current_interval == 1:
            next_interval = 6
        else:
            next_interval = int(current_interval * new_ease)
            
    return next_interval, new_ease
