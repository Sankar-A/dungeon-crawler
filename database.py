"""
Database module for persistent storage
Uses PostgreSQL with SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from datetime import datetime
from config import Config
import logging
import bcrypt
import sys
import traceback

logger = logging.getLogger(__name__)

Base = declarative_base()

class User(Base):
    """User account for login"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    username_lower = Column(String(50), unique=True, nullable=False, index=True)  # For case-insensitive lookups
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship to characters
    characters = relationship('PlayerData', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert to dictionary (without password)"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'character_count': len(self.characters) if self.characters else 0
        }

class PlayerData(Base):
    """Persistent player data storage"""
    __tablename__ = 'players'
    
    id = Column(String, primary_key=True)  # player_id (socket session id)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable for backward compatibility
    name = Column(String(10), nullable=False)  # Character name (max 10 chars)
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
    
    # Relationship to user
    user = relationship('User', back_populates='characters')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
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
                logger.info("Initializing database connection...")
                
                # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
                database_url = Config.DATABASE_URL
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace('postgres://', 'postgresql://', 1)
                    logger.info("Converted postgres:// to postgresql:// for SQLAlchemy")
                
                # Log connection attempt (without exposing password)
                safe_url = database_url.split('@')[-1] if '@' in database_url else 'local'
                logger.info(f"Connecting to database: {safe_url}")
                
                self.engine = create_engine(
                    database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False
                )
                
                logger.info("Database engine created successfully")
                
                self.Session = scoped_session(sessionmaker(bind=self.engine))
                logger.info("Session factory created")
                
                # Create tables (will not recreate existing ones)
                try:
                    logger.info("Creating/updating database schema...")
                    Base.metadata.create_all(self.engine)
                    logger.info("Database schema initialized successfully")
                    
                    # Run migration for username_lower column if needed
                    self._migrate_username_lower()
                    
                    if self.is_dev:
                        print(f"[DEV] Database initialized")
                    else:
                        logger.info("Database initialized successfully")
                except Exception as schema_error:
                    logger.warning(f"Schema creation warning: {schema_error}")
                    logger.warning(f"Traceback: {traceback.format_exc()}")
                    # Continue anyway - tables might already exist
                    if not self.is_dev:
                        logger.info("Continuing with existing schema")
                
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                if self.is_dev:
                    print(f"[DEV] Database initialization failed: {e} (will simulate operations)")
                else:
                    logger.error("Database will be disabled")
                
                self.enabled = False
    
    def get_session(self):
        """Get a database session"""
        if not self.enabled:
            return None
        return self.Session()
    
    def _migrate_username_lower(self):
        """Migrate existing users table to add username_lower column"""
        try:
            from sqlalchemy import text
            session = self.get_session()
            
            # Check if column already exists
            result = session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='username_lower'
            """))
            
            if result.fetchone():
                session.close()
                return  # Column already exists
            
            logger.info("Migrating users table: adding username_lower column...")
            
            # Add the column
            session.execute(text("ALTER TABLE users ADD COLUMN username_lower VARCHAR(50)"))
            
            # Populate with lowercase usernames
            session.execute(text("UPDATE users SET username_lower = LOWER(username)"))
            
            # Make it NOT NULL
            session.execute(text("ALTER TABLE users ALTER COLUMN username_lower SET NOT NULL"))
            
            # Add unique constraint
            session.execute(text("ALTER TABLE users ADD CONSTRAINT users_username_lower_key UNIQUE (username_lower)"))
            
            # Add index
            session.execute(text("CREATE INDEX IF NOT EXISTS ix_users_username_lower ON users (username_lower)"))
            
            session.commit()
            session.close()
            
            logger.info("Migration completed: username_lower column added successfully")
            
        except Exception as e:
            logger.warning(f"Migration skipped or failed (may already be applied): {e}")
            if session:
                session.rollback()
                session.close()
    
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
                # Create new (should not happen with new auth flow, but keep for safety)
                # Allow None user_id for backward compatibility
                player_data = PlayerData(
                    id=player_obj.id,
                    user_id=player_obj.user_id if hasattr(player_obj, 'user_id') else None,
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
    
    def create_user(self, username, password):
        """Create a new user account"""
        if not self.enabled:
            return None
        
        try:
            session = self.get_session()
            
            # Normalize username for case-insensitive check
            username_lower = username.lower()
            
            # Check if username exists (case-insensitive)
            existing = session.query(User).filter_by(username_lower=username_lower).first()
            if existing:
                session.close()
                if self.is_dev:
                    print(f"[DEV] DB CREATE USER FAILED: {username} already exists (found as '{existing.username}')")
                logger.info(f"Registration failed: username '{username}' already taken")
                return None
            
            # Create user
            user = User(username=username, username_lower=username_lower)
            user.set_password(password)
            session.add(user)
            session.commit()
            
            user_dict = user.to_dict()
            session.close()
            
            if self.is_dev:
                print(f"[DEV] DB CREATE USER SUCCESS: {username} (ID: {user_dict['id']})")
            logger.info(f"User created successfully: {username} (ID: {user_dict['id']})")
            
            return user_dict
        except Exception as e:
            logger.error(f"Failed to create user '{username}': {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate user and return user data"""
        if not self.enabled:
            return None
        
        try:
            session = self.get_session()
            
            # Case-insensitive username lookup
            username_lower = username.lower()
            user = session.query(User).filter_by(username_lower=username_lower, is_active=True).first()
            
            if user and user.check_password(password):
                user.last_login = datetime.utcnow()
                session.commit()
                user_dict = user.to_dict()
                session.close()
                
                if self.is_dev:
                    print(f"[DEV] DB AUTH SUCCESS: {username} (ID: {user_dict['id']})")
                logger.info(f"User authenticated: {username}")
                
                return user_dict
            
            session.close()
            
            if self.is_dev:
                print(f"[DEV] DB AUTH FAILED: {username} - invalid credentials")
            logger.info(f"Authentication failed for username: {username}")
            
            return None
        except Exception as e:
            logger.error(f"Failed to authenticate user '{username}': {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            if session:
                session.close()
            return None
    
    def get_user_characters(self, user_id):
        """Get all characters for a user"""
        if not self.enabled:
            return []
        
        if self.is_dev:
            print(f"[DEV] DB QUERY: Characters for user {user_id}")
            return []  # Simulate empty list in dev
        
        try:
            session = self.get_session()
            characters = session.query(PlayerData)\
                .filter_by(user_id=user_id, is_active=True)\
                .order_by(PlayerData.last_login.desc())\
                .all()
            
            char_list = [c.to_dict() for c in characters]
            session.close()
            return char_list
        except Exception as e:
            logger.error(f"Failed to get user characters: {e}")
            if session:
                session.close()
            return []
    
    def create_character(self, user_id, character_name, player_id):
        """Create a new character for a user"""
        if not self.enabled:
            return None
        
        if self.is_dev:
            print(f"[DEV] DB CREATE CHARACTER: {character_name} for user {user_id}")
            return True  # Simulate success in dev
        
        try:
            session = self.get_session()
            
            # Check character limit (10 per user) - only if user_id is provided
            if user_id:
                char_count = session.query(PlayerData).filter_by(user_id=user_id, is_active=True).count()
                if char_count >= 10:
                    session.close()
                    return None
                
                # Check if character name is taken by this user
                existing = session.query(PlayerData).filter_by(user_id=user_id, name=character_name).first()
                if existing:
                    session.close()
                    return None
            
            # Create character
            character = PlayerData(
                id=player_id,
                user_id=user_id,
                name=character_name
            )
            session.add(character)
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Failed to create character: {e}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def delete_character(self, user_id, character_name):
        """Delete a character (soft delete)"""
        if not self.enabled:
            return False
        
        if self.is_dev:
            print(f"[DEV] DB DELETE CHARACTER: {character_name} for user {user_id}")
            return True  # Simulate success in dev
        
        try:
            session = self.get_session()
            character = session.query(PlayerData)\
                .filter_by(user_id=user_id, name=character_name, is_active=True)\
                .first()
            
            if character:
                character.is_active = False
                session.commit()
                session.close()
                return True
            
            session.close()
            return False
        except Exception as e:
            logger.error(f"Failed to delete character: {e}")
            if session:
                session.rollback()
                session.close()
            return False


# Global database instance
db = Database()
