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
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    messages = relationship('Message', back_populates='session', cascade='all, delete-orphan')
    
    def to_dict(self, include_messages=False):
        """Convert session to dictionary."""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'model_name': self.model_name,
            'created_at': self.created_at.isoformat()
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
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
