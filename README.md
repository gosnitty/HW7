# Distributed Task Processing System

## Task 3&4
https://docs.google.com/document/d/1SZ2XEThhYVqcYY7SzStsBaa5O3twWhzRDMdsokFiCPY/edit?usp=sharing

## System Overview
A Flask-based web service with Celery for asynchronous task processing, featuring comprehensive logging and alerting.

## Key Features
- HTTP API endpoint for task submission
- Background task processing
- Real-time progress tracking
- Automated error alerts

## Installation

### Prerequisites
- Python 3.10+
- Redis server
- Virtual environment (recommended)

## Running the System
  Start Redis:
    redis-server

  Start Celery workers (in separate terminals):
    celery -A app1.tasks worker --loglevel=info --hostname=worker1@%h --pool=solo
    celery -A app1.tasks worker --loglevel=info --hostname=worker2@%h --pool=solo
    
  Start Flask application:
    python app1/main.py
