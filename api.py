from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from datetime import date


from database import get_db, initialize_db
from models import Player, PlayerPosition, InjuryStatus, Match, SquadPlan, SquadRole, TrainingPlan, MatchStat, \
    MatchResult
from schemas import (
    PlayerCreate, PlayerRead,
    MatchCreate, MatchRead, MatchUpdateResult,
    MatchStatCreate, MatchStatRead,
    SquadPlanBase, SquadPlanRead
)


app = FastAPI(
    title="Vietnamese Football Team Management System (V-League)",
    version="1.0.0",
    description="Backend API for managing players, squads, matches, and analytics for a V-League team.",
)


def calculate_match_result(our_score: int, opponent_score: int) -> MatchResult:
    """Determines the match result based on scores."""
    if our_score > opponent_score:
        return MatchResult.W
    elif our_score < opponent_score:
        return MatchResult.L
    else:
        return MatchResult.D


def calculate_pass_success_rate(total: int, successful: int) -> float:
    """Calculates pass success rate as a percentage."""
    if total == 0:
        return 0.0
    return round((successful / total) * 100, 2)




@app.post("/players/", response_model=PlayerRead, status_code=status.HTTP_201_CREATED, tags=["Players"])
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    db_player = Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@app.get("/players/", response_model=List[PlayerRead], tags=["Players"])
def get_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = db.query(Player).offset(skip).limit(limit).all()
    return players


@app.get("/players/{player_id}", response_model=PlayerRead, tags=["Players"])
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.post("/matches/", response_model=MatchRead, status_code=status.HTTP_201_CREATED, tags=["Matches & Schedules"])
def schedule_match(match: MatchCreate, db: Session = Depends(get_db)):
    """Schedule a new match in the tournament."""
    if match.match_date < date.today() and not match.is_completed:
        raise HTTPException(status_code=400, detail="Cannot schedule a future match as completed.")

    db_match = Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@app.get("/matches/upcoming", response_model=List[MatchRead], tags=["Matches & Schedules"])
def get_upcoming_matches(db: Session = Depends(get_db)):
    # Note: Sorting and filtering is done on the application side to avoid complex index requirements in the database
    matches = db.query(Match).filter(Match.is_completed == False).all()

    # Sort them by date in Python (due to the system instruction constraint)
    sorted_matches = sorted(matches, key=lambda m: m.match_date)
    return sorted_matches


@app.put("/matches/{match_id}/result", response_model=MatchRead, tags=["Matches & Schedules"])
def update_match_result(match_id: int, result_data: MatchUpdateResult, db: Session = Depends(get_db)):
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")


    db_match.is_completed = True
    db_match.our_score = result_data.our_score
    db_match.opponent_score = result_data.opponent_score
    db_match.result = calculate_match_result(db_match.our_score, db_match.opponent_score)
    db.commit()
    db.refresh(db_match)
    return db_match


@app.post("/matches/{match_id}/squad", response_model=SquadPlanRead, tags=["Squad & Tactics"])
def set_squad_plan(match_id: int, squad_plan: SquadPlanBase, db: Session = Depends(get_db)):
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")


    db_squad = db.query(SquadPlan).filter(SquadPlan.match_id == match_id).first()

    if db_squad:
        db.query(SquadRole).filter(SquadRole.squad_plan_id == db_squad.id).delete()
        db.flush()
    else:
        db_squad = SquadPlan(
            match_id=match_id,
            formation=squad_plan.formation,
            tactics_notes=squad_plan.tactics_notes
        )
        db.add(db_squad)
        db.flush()

    for role in squad_plan.roles:
        if not db.query(Player).filter(Player.id == role.player_id).first():
            raise HTTPException(status_code=400, detail=f"Player ID {role.player_id} not found.")

        db_role = SquadRole(
            squad_plan_id=db_squad.id,
            player_id=role.player_id,
            is_starter=role.is_starter,
            specific_role=role.specific_role
        )
        db.add(db_role)

    db.commit()
    db.refresh(db_squad)
    return db_squad


@app.post("/matches/{match_id}/stats", response_model=MatchStatRead, status_code=status.HTTP_201_CREATED,
          tags=["Data Analysis"])
def add_match_statistics(match_id: int, stats: MatchStatCreate, db: Session = Depends(get_db)):
    """Add detailed statistics for a completed match."""
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if db_match is None or not db_match.is_completed:
        raise HTTPException(status_code=400, detail="Statistics can only be added to a completed match that exists.")

    if db.query(MatchStat).filter(MatchStat.match_id == match_id).first():
        raise HTTPException(status_code=400, detail="Statistics already exist for this match. Use PUT to update.")

    pass_success_rate = calculate_pass_success_rate(stats.total_passes, stats.successful_passes)
    db_stats = MatchStat(
        match_id=match_id,
        pass_success_rate=pass_success_rate,
        **stats.model_dump()
    )

    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats


@app.get("/matches/{match_id}/stats", response_model=MatchStatRead, tags=["Data Analysis"])
def get_match_statistics(match_id: int, db: Session = Depends(get_db)):
    stats = db.query(MatchStat).filter(MatchStat.match_id == match_id).first()
    if stats is None:
        raise HTTPException(status_code=404, detail="Statistics not found for this match.")
    return stats