"""
Database models for the Unlearning to Rest User Study.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model - identified by email only."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Session(Base):
    """Chat session model - represents one conversation with a specific model."""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    model_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    context_reset_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    messages = relationship('Message', back_populates='session', cascade='all, delete-orphan')
    prompts = relationship('Prompt', back_populates='session', cascade='all, delete-orphan')
    generated_images = relationship('GeneratedImage', back_populates='session', cascade='all, delete-orphan')
    
    def to_dict(self, include_messages=False):
        """Convert session to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat(),
            'context_reset_at': (self.context_reset_at or self.created_at).isoformat()
        }
        if include_messages:
            data['messages'] = [msg.to_dict() for msg in self.messages]
        return data


class Message(Base):
    """Message model - represents a single message in a chat session."""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    prompts = relationship('Prompt', back_populates='source_message', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }


class Prompt(Base):
    """Prompt model - captures participant-created image generation prompts for a session."""
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False, index=True)
    title = Column(String(150), nullable=True)
    content = Column(Text, nullable=False)
    source_message_id = Column(Integer, ForeignKey('messages.id'), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    # Relationships
    session = relationship('Session', back_populates='prompts')
    source_message = relationship('Message', back_populates='prompts')
    generated_images = relationship('GeneratedImage', back_populates='prompt', cascade='all, delete-orphan')

    def to_dict(self):
        """Convert prompt to dictionary."""
        excerpt = None
        source_role = None
        if self.source_message:
            excerpt = self.source_message.content[:200]
            source_role = self.source_message.role

        return {
            'id': self.id,
            'session_id': self.session_id,
            'title': self.title,
            'content': self.content,
            'source_message_id': self.source_message_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'source_message_excerpt': excerpt,
            'source_message_role': source_role
        }


class GeneratedImage(Base):
    """GeneratedImage model - stores information about images generated from prompts."""
    __tablename__ = 'generated_images'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False, index=True)
    prompt_id = Column(Integer, ForeignKey('prompts.id'), nullable=False, index=True)
    image_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship('Session', back_populates='generated_images')
    prompt = relationship('Prompt', back_populates='generated_images')

    def to_dict(self):
        """Convert generated image to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'prompt_id': self.prompt_id,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat(),
            'prompt_content': self.prompt.content if self.prompt else None
        }

