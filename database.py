"""
Database module for persistent storage
Uses PostgreSQL with SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

class PlayerData(Base):
    """Persistent player data storage"""
    __tablename__ = 'players'
    
    id = Column(String, primary_key=True)  # player_id (socket session id)
    name = Column(String, nullable=False)
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    gold = Column(Integer, default=0)
    floor = Column(Integer, default=1)
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    hp = Column(Integer, default=100)
    max_hp = Column(Integer, default=100)
    
    # Equipment (stored as JSON)
    weapon = Column(JSON, nullable=True)
    armor = Column(JSON, nullable=True)
    
    # Skills (stored as JSON)
    skills = Column(JSON, default=dict)
    skill_points = Column(Integer, default=0)
    
    # Inventory (stored as JSON array)
    inventory = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'xp': self.xp,
            'gold': self.gold,
            'floor': self.floor,
            'x': self.x,
            'y': self.y,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'weapon': self.weapon,
            'armor': self.armor,
            'skills': self.skills,
            'skill_points': self.skill_points,
            'inventory': self.inventory,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class GameStats(Base):
    """Game statistics and leaderboard"""
    __tablename__ = 'game_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, nullable=False)
    player_name = Column(String, nullable=False)
    
    # Stats
    total_kills = Column(Integer, default=0)
    total_damage = Column(Integer, default=0)
    floors_reached = Column(Integer, default=1)
    deaths = Column(Integer, default=0)
    playtime_seconds = Column(Integer, default=0)
    
    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """Database manager"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.enabled = Config.DATABASE_ENABLED
        self.is_dev = Config.FLASK_ENV == 'development'
        
        if self.enabled:
            try:
                # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
                database_url = Config.DATABASE_URL
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace('postgres://', 'postgresql://', 1)
                
                self.engine = create_engine(
                    database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False
                )
                self.Session = scoped_session(sessionmaker(bind=self.engine))
                Base.metadata.create_all(self.engine)
                
                if self.is_dev:
                    print(f"[DEV] Database initialized (operations will be simulated)")
                else:
                    logger.info("Database initialized successfully")
            except Exception as e:
                if self.is_dev:
                    print(f"[DEV] Database initialization failed: {e} (will simulate operations)")
                else:
                    logger.error(f"Database initialization failed: {e}")
                self.enabled = False
    
    def get_session(self):
        """Get a database session"""
        if not self.enabled:
            return None
        return self.Session()
    
    def save_player(self, player_obj):
        """Save or update player data"""
        if not self.enabled:
            return False
        
        if self.is_dev:
            print(f"[DEV] DB SAVE: Player {player_obj.name} (Level {player_obj.level}, Floor {player_obj.floor})")
            return True  # Simulate success in dev
        
        try:
            session = self.get_session()
            player_data = session.query(PlayerData).filter_by(id=player_obj.id).first()
            
            if player_data:
                # Update existing
                player_data.name = player_obj.name
                player_data.level = player_obj.level
                player_data.xp = player_obj.xp
                player_data.gold = player_obj.gold
                player_data.floor = player_obj.floor
                player_data.x = player_obj.x
                player_data.y = player_obj.y
                player_data.hp = player_obj.hp
                player_data.max_hp = player_obj.max_hp
                player_data.weapon = player_obj.weapon
                player_data.armor = player_obj.armor
                player_data.skills = player_obj.skills
                player_data.skill_points = player_obj.skill_points
                player_data.last_login = datetime.utcnow()
            else:
                # Create new
                player_data = PlayerData(
                    id=player_obj.id,
                    name=player_obj.name,
                    level=player_obj.level,
                    xp=player_obj.xp,
                    gold=player_obj.gold,
                    floor=player_obj.floor,
                    x=player_obj.x,
                    y=player_obj.y,
                    hp=player_obj.hp,
                    max_hp=player_obj.max_hp,
                    weapon=player_obj.weapon,
                    armor=player_obj.armor,
                    skills=player_obj.skills,
                    skill_points=player_obj.skill_points
                )
                session.add(player_data)
            
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Failed to save player: {e}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def load_player(self, player_id):
        """Load player data from database"""
        if not self.enabled:
            return None
        
        if self.is_dev:
            print(f"[DEV] DB LOAD: Player {player_id}")
            return None  # Simulate not found in dev
        
        try:
            session = self.get_session()
            player_data = session.query(PlayerData).filter_by(id=player_id).first()
            session.close()
            return player_data.to_dict() if player_data else None
        except Exception as e:
            logger.error(f"Failed to load player: {e}")
            if session:
                session.close()
            return None
    
    def get_leaderboard(self, limit=10):
        """Get top players by level and XP"""
        if not self.enabled:
            return []
        
        if self.is_dev:
            print(f"[DEV] DB QUERY: Leaderboard (limit {limit})")
            return []  # Simulate empty leaderboard in dev
        
        try:
            session = self.get_session()
            players = session.query(PlayerData)\
                .filter_by(is_active=True)\
                .order_by(PlayerData.level.desc(), PlayerData.xp.desc())\
                .limit(limit)\
                .all()
            
            leaderboard = [p.to_dict() for p in players]
            session.close()
            return leaderboard
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            if session:
                session.close()
            return []
    
    def close(self):
        """Close database connections"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()


# Global database instance
db = Database()
