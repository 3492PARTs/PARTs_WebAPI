"""
Scouting repository interfaces.

Defines contracts for scouting data access operations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet

from core.interfaces.repository import IRepository


class IScoutingRepository(IRepository):
    """
    Interface for scouting data access operations.
    """
    
    @abstractmethod
    def get_current_season(self) -> Optional[Any]:
        """
        Get the current active season.
        
        Returns:
            Current season if exists, None otherwise
        """
        pass
    
    @abstractmethod
    def get_field_responses(
        self,
        season_id: int,
        team_id: Optional[int] = None,
        match_id: Optional[int] = None
    ) -> QuerySet:
        """
        Get field scouting responses filtered by criteria.
        
        Args:
            season_id: The season ID
            team_id: Optional team ID filter
            match_id: Optional match ID filter
            
        Returns:
            QuerySet of field responses
        """
        pass
    
    @abstractmethod
    def get_field_schedule(
        self,
        season_id: int,
        team_id: Optional[int] = None
    ) -> QuerySet:
        """
        Get field schedule for a season.
        
        Args:
            season_id: The season ID
            team_id: Optional team ID filter
            
        Returns:
            QuerySet of schedule entries
        """
        pass
    
    @abstractmethod
    def create_field_response(self, **kwargs) -> Any:
        """
        Create a new field scouting response.
        
        Args:
            **kwargs: Response attributes
            
        Returns:
            Created response object
        """
        pass
    
    @abstractmethod
    def get_question_aggregates(self, form_type: str, season_id: int) -> QuerySet:
        """
        Get question aggregates for a form type and season.
        
        Args:
            form_type: Type of form (e.g., 'field', 'pit')
            season_id: The season ID
            
        Returns:
            QuerySet of question aggregates
        """
        pass
    
    @abstractmethod
    def get_team_rankings(self, season_id: int) -> List[Dict[str, Any]]:
        """
        Get team rankings for a season.
        
        Args:
            season_id: The season ID
            
        Returns:
            List of team ranking dictionaries
        """
        pass
