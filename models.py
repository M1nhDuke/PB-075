from sqlalchemy import Column, Integer, String, Float, Date, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import date
import enum


# Define Enums for consistent data types
class PlayerPosition(enum.Enum):
    GK = "Goalkeeper"
    CB = "Center Back"
    LB = "Left Back"
    RB = "Right Back"
    DM = "Defensive Midfielder"
    CM = "Center Midfielder"
    AM = "Attacking Midfielder"
    LW = "Left Winger"
    RW = "Right Winger"
    ST = "Striker"


class InjuryStatus(enum.Enum):
    FIT = "Fit"
    MINOR = "Minor Injury"
    LONG_TERM = "Long Term Injury"
    SUSPENDED = "Suspended"


class MatchResult(enum.Enum):
    W = "Win"
    D = "Draw"
    L = "Loss"


# --- CORE MODELS ---

class Player(Base):
    """Represents a player in the team."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    position = Column(Enum(PlayerPosition), nullable=False)
    jersey_number = Column(Integer, unique=True, nullable=False)

    # Financial and Status
    transfer_price_vnd = Column(Float, default=0.0)  # Price in VND
    injury_status = Column(Enum(InjuryStatus), default=InjuryStatus.FIT)

    # Relationships
    squad_roles = relationship("SquadRole", back_populates="player")


class Match(Base):
    """Represents a scheduled or completed match."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_date = Column(Date, nullable=False)
    opponent_name = Column(String(100), nullable=False)
    venue = Column(String(100))  # Home or Away
    is_completed = Column(Boolean, default=False)
    our_score = Column(Integer, default=0)
    opponent_score = Column(Integer, default=0)
    result = Column(Enum(MatchResult), nullable=True)  # Calculated after completion

    # Relationships
    squad_plan = relationship("SquadPlan", uselist=False, back_populates="match")
    training_plan = relationship("TrainingPlan", uselist=False, back_populates="match")
    match_stats = relationship("MatchStat", uselist=False, back_populates="match")


class SquadPlan(Base):
    """Defines the starting lineup and bench for a specific match."""
    __tablename__ = "squad_plans"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)
    formation = Column(String(10), default="4-3-3")  # e.g., '4-3-3', '3-5-2'
    tactics_notes = Column(Text)

    # Relationships
    match = relationship("Match", back_populates="squad_plan")
    roles = relationship("SquadRole", back_populates="squad_plan", cascade="all, delete-orphan")


class SquadRole(Base):
    """Links a Player to a SquadPlan and defines their role (Starter/Bench)."""
    __tablename__ = "squad_roles"

    id = Column(Integer, primary_key=True, index=True)
    squad_plan_id = Column(Integer, ForeignKey("squad_plans.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    is_starter = Column(Boolean, default=True)  # True for starter, False for bench
    specific_role = Column(String(50), nullable=True)  # e.g., 'Target Man', 'False 9'

    # Relationships
    squad_plan = relationship("SquadPlan", back_populates="roles")
    player = relationship("Player", back_populates="squad_roles")


class TrainingPlan(Base):
    """Stores training plans and general tactics notes for an upcoming match."""
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)
    plan_name = Column(String(100), nullable=False)
    focus_areas = Column(Text)  # e.g., 'Defensive set pieces', 'High press transition'
    last_updated = Column(Date, default=date.today)

    # Relationships
    match = relationship("Match", back_populates="training_plan")


class MatchStat(Base):
    """Detailed match statistics for data analysis."""
    __tablename__ = "match_stats"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)

    # Expected Goals (xG) and shooting metrics
    expected_goals = Column(Float, default=0.0)
    shots_on_target = Column(Integer, default=0)

    # Passing and Possession
    ball_possession_percent = Column(Float, default=0.0)  # Percentage
    total_passes = Column(Integer, default=0)
    successful_passes = Column(Integer, default=0)
    pass_success_rate = Column(Float, default=0.0)  # Calculated

    # Defensive metrics
    interceptions = Column(Integer, default=0)
    successful_tackles = Column(Integer, default=0)
    aerial_disputes_won = Column(Integer, default=0)

    # Match meta data
    total_fouls = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    # Relationships
    match = relationship("Match", back_populates="match_stats")