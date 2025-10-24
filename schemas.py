from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import List, Optional
from models import PlayerPosition, InjuryStatus, MatchResult


# --- Base Pydantic Configuration for SQLAlchemy ORM ---
# Enables Pydantic to read data from SQLAlchemy objects
# This is equivalent to orm_mode = True in Pydantic v1
class Config:
    model_config = ConfigDict(from_attributes=True)


# --- PLAYER SCHEMAS ---
class PlayerBase(BaseModel):
    name: str = Field(..., max_length=100)
    age: int = Field(..., ge=18, le=45)
    date_of_birth: date
    position: PlayerPosition
    jersey_number: int
    transfer_price_vnd: float = 0.0
    injury_status: InjuryStatus = InjuryStatus.FIT


class PlayerCreate(PlayerBase):
    """Schema for creating a new player."""
    pass


class PlayerRead(PlayerBase):
    """Schema for reading player data, includes ID."""
    id: int

    # Add Pydantic config
    model_config = Config


# --- MATCH STAT SCHEMAS (nested in Match) ---
class MatchStatBase(BaseModel):
    expected_goals: float = 0.0
    shots_on_target: int = 0
    ball_possession_percent: float = Field(0.0, ge=0.0, le=100.0)
    total_passes: int = 0
    successful_passes: int = 0
    interceptions: int = 0
    successful_tackles: int = 0
    aerial_disputes_won: int = 0
    total_fouls: int = 0
    yellow_cards: int = 0
    red_cards: int = 0


class MatchStatCreate(MatchStatBase):
    pass


class MatchStatRead(MatchStatBase):
    id: int
    pass_success_rate: float  # This is calculated in the model/service
    model_config = Config


# --- SQUAD & TRAINING SCHEMAS (nested in Match) ---
class SquadRoleBase(BaseModel):
    player_id: int
    is_starter: bool
    specific_role: Optional[str] = None


class SquadRoleRead(SquadRoleBase):
    id: int
    player: PlayerRead  # Nested player information
    model_config = Config


class SquadPlanBase(BaseModel):
    formation: str
    tactics_notes: Optional[str] = None
    roles: List[SquadRoleBase]  # List of players/roles


class SquadPlanRead(SquadPlanBase):
    id: int
    roles: List[SquadRoleRead]  # List of fully populated roles
    model_config = Config


class TrainingPlanBase(BaseModel):
    plan_name: str
    focus_areas: Optional[str] = None
    last_updated: Optional[date] = None


class TrainingPlanRead(TrainingPlanBase):
    id: int
    model_config = Config


# --- MATCH SCHEMAS ---
class MatchBase(BaseModel):
    match_date: date
    opponent_name: str
    venue: str
    is_completed: bool = False
    our_score: int = 0
    opponent_score: int = 0
    result: Optional[MatchResult] = None


class MatchCreate(MatchBase):
    pass


class MatchRead(MatchBase):
    id: int

    # Relationships for complex data
    squad_plan: Optional[SquadPlanRead] = None
    training_plan: Optional[TrainingPlanRead] = None
    match_stats: Optional[MatchStatRead] = None

    model_config = Config


class MatchUpdateResult(MatchBase):
    """Schema for updating match score and completion status."""
    is_completed: bool = True
    our_score: int
    opponent_score: int
    result: Optional[MatchResult] = None  # Will be calculated by the backend logic
