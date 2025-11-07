"""
DTOs for the scouting domain.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class SeasonDTO:
    """Data transfer object for season information."""
    id: int
    year: int
    is_current: bool
    game_name: Optional[str] = None


@dataclass
class FieldResponseDTO:
    """Data transfer object for field scouting response."""
    id: int
    season_id: int
    team_id: int
    match_number: int
    responses: Dict[str, Any]
    created_at: datetime
    user_id: int


@dataclass
class CreateFieldResponseDTO:
    """Data transfer object for creating a field response."""
    season_id: int
    team_id: int
    match_number: int
    responses: Dict[str, Any]
    user_id: int


@dataclass
class TeamRankingDTO:
    """Data transfer object for team ranking."""
    team_id: int
    team_name: str
    rank: int
    total_score: float
    matches_played: int
    stats: Dict[str, Any]


@dataclass
class QuestionAggregateDTO:
    """Data transfer object for question aggregate."""
    id: int
    question_text: str
    question_type: str
    order: int
    form_type: str
    season_id: int


@dataclass
class FieldScheduleDTO:
    """Data transfer object for field schedule entry."""
    id: int
    match_number: int
    team_id: int
    alliance_color: str
    season_id: int
    competition_id: Optional[int] = None
