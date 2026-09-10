# StudyFlow AI - Architecture & Design Document

## 1. System Overview

StudyFlow AI is an intelligent calendar and study-management application designed specifically for students. It combines:
- **Real-time scheduling engine** that automatically rescheduling tasks based on conflicts and delays
- **Spaced repetition algorithm** for optimal learning retention
- **AI-powered task breakdown** that distributes workload intelligently across days
- **Cross-platform mobile app** with real-time synchronization

---

## 2. Tech Stack

### Frontend (Mobile)
- **Framework:** React Native with Expo
- **State Management:** Redux Toolkit
- **Real-time Updates:** WebSocket (Socket.io)
- **Local Storage:** AsyncStorage + SQLite (offline-first)
- **UI Components:** React Native Paper
- **Calendar Library:** react-native-calendars + custom scheduling visualization
- **Push Notifications:** Expo Notifications

### Backend
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.0
- **Real-time:** FastAPI WebSocket + Socket.io
- **Task Queue:** Celery + Redis
- **Authentication:** JWT + OAuth2
- **API Docs:** Swagger/OpenAPI

### DevOps & Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose (dev), Kubernetes (prod)
- **Hosting:** AWS/GCP/DigitalOcean
- **Database:** PostgreSQL with replication
- **Caching:** Redis
- **Queue:** Celery Workers
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack

---

## 3. Database Schema

### Core Entities

```
users
├── id (UUID, PK)
├── email (unique)
├── username (unique)
├── password_hash
├── timezone
├── study_start_hour (9)
├── study_end_hour (21)
├── daily_study_hours (int)
├── created_at
└── updated_at

subjects/folders
├── id (UUID, PK)
├── user_id (FK)
├── name (e.g., "AP Biology")
├── color
├── icon
├── created_at
└── updated_at

assignments/tasks
├── id (UUID, PK)
├── user_id (FK)
├── subject_id (FK)
├── title
├── description
├── due_date (datetime)
├── difficulty (EASY/MEDIUM/HARD)
├── estimated_hours (computed)
├── status (NOT_STARTED/IN_PROGRESS/COMPLETED)
├── created_at
└── updated_at

scheduled_sessions
├── id (UUID, PK)
├── assignment_id (FK)
├── user_id (FK)
├── start_time (datetime)
├── end_time (datetime)
├── session_type (STUDY/REVIEW/QUIZ)
├── status (SCHEDULED/IN_PROGRESS/COMPLETED/SKIPPED)
├── created_at
└── updated_at

calendar_events
├── id (UUID, PK)
├── user_id (FK)
├── title
├── start_time (datetime)
├── end_time (datetime)
├── event_type (FIXED/STUDY_SESSION/EXAM)
├── is_recurring
├── created_at
└── updated_at

spaced_repetition_log
├── id (UUID, PK)
├── assignment_id (FK)
├── user_id (FK)
├── review_number (1, 2, 3...)
├── scheduled_date (datetime)
├── completed_date (datetime, nullable)
├── retention_score (0-100)
├── created_at
└── updated_at

quiz_questions
├── id (UUID, PK)
├── assignment_id (FK)
├── question_text
├── answer_options (JSON)
├── correct_answer
├── difficulty_level
├── created_at
└── updated_at

quiz_responses
├── id (UUID, PK)
├── user_id (FK)
├── question_id (FK)
├── selected_answer
├── is_correct
├── response_time_seconds
├── created_at
└── updated_at
```

---

## 4. Core Algorithms

### 4.1 Task Breakdown Algorithm
```
Input: Assignment (title, due_date, difficulty, estimated_hours)
Output: List of scheduled daily micro-sessions

Process:
1. Calculate days until deadline
2. Determine session duration (45-90 min based on difficulty)
3. Account for user's available study hours per day
4. Distribute workload:
   - HARD: 70% in first 50% of time, 30% spread after
   - MEDIUM: 50-50 split across timeline
   - EASY: Can be compressed later
5. Create daily study sessions, respecting:
   - User's study hours (e.g., 9 AM - 9 PM)
   - Existing calendar conflicts
   - Break time between sessions
6. Return array of (date, start_time, duration, session_type)
```

### 4.2 Scheduling Engine (Real-Time Recalculation)
```
Triggered by:
- Conflict detection (new event added to calendar)
- Task delay (session marked incomplete)
- User rescheduling a session

Process:
1. Identify affected assignments (those with overlapping sessions)
2. Free up the affected time slots
3. Re-run Task Breakdown Algorithm for each affected task
4. Attempt to pack sessions into available slots
5. If unable to fit: 
   - Extend deadline or reduce scope (notify user)
   - Suggest user delete/defer lower-priority tasks
6. Push notification: "Your schedule changed! Review updated study plan"
```

### 4.3 Spaced Repetition Schedule
```
Based on: Ebbinghaus Curve + Active Recall

Intervals (in days):
- Day 0: Initial learning session
- Day 1: First review (24h after)
- Day 3: Second review (72h after)
- Day 7: Third review (1 week)
- Day 14: Fourth review (2 weeks)
- Day 30: Fifth review (30 days)

For each assignment:
1. Create review sessions at calculated intervals
2. Schedule with lower priority than new material
3. Auto-reschedule if user misses review
4. Quiz difficulty increases if retention_score > 80%
5. If retention_score < 60%, add extra review before next interval
```

### 4.4 Smart Notification System
```
Notification Types:
1. Upcoming Session: 15 min before
2. Daily Digest: 8 AM (summary of day's tasks)
3. Missed Session Alert: 2h after missed session
4. Focus Time Blocked: When entering study hour
5. Conflict Warning: When scheduling conflict detected
6. Exam Prep Alert: 1 week before exam

Delivery:
- Push notifications (mobile)
- In-app alerts
- Email digest (weekly)
- SMS for critical deadlines
```

---

## 5. API Endpoints

### Authentication
- `POST /auth/register` - Register user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout

### Users
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update profile
- `PUT /users/settings` - Update study hours, timezone, etc.

### Subjects/Folders
- `GET /subjects` - List all subjects
- `POST /subjects` - Create subject
- `PUT /subjects/{id}` - Update subject
- `DELETE /subjects/{id}` - Delete subject

### Assignments
- `GET /assignments` - List assignments (with filters)
- `POST /assignments` - Create assignment (triggers scheduling)
- `PUT /assignments/{id}` - Update assignment
- `DELETE /assignments/{id}` - Delete assignment
- `POST /assignments/{id}/complete` - Mark complete

### Scheduled Sessions
- `GET /sessions` - List sessions (calendar view)
- `GET /sessions/{id}` - Get session details
- `PUT /sessions/{id}` - Reschedule session
- `POST /sessions/{id}/start` - Start session
- `POST /sessions/{id}/complete` - Complete session
- `POST /sessions/{id}/skip` - Skip session

### Calendar Events
- `GET /calendar/events` - Get calendar events (date range)
- `POST /calendar/events` - Add calendar event (triggers reschedule)
- `PUT /calendar/events/{id}` - Update event
- `DELETE /calendar/events/{id}` - Delete event

### Spaced Repetition
- `GET /repetition/schedule` - Get review schedule
- `POST /repetition/{assignment_id}/review` - Record review session

### Quiz
- `GET /quiz/{assignment_id}/questions` - Get practice questions
- `POST /quiz/response` - Submit quiz response
- `GET /quiz/analytics` - Get quiz analytics

### Real-time WebSocket
- `ws://api.studyflow.ai/ws/calendar` - Real-time calendar updates
- `ws://api.studyflow.ai/ws/notifications` - Real-time notifications

---

## 6. Project Structure

```
studyflow-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   └── utils.py
│   │   ├── users/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routes.py
│   │   ├── subjects/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routes.py
│   │   ├── assignments/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   └── services.py
│   │   ├── scheduling/
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py
│   │   │   ├── algorithms.py
│   │   │   └── notifications.py
│   │   ├── spaced_repetition/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── algorithms.py
│   │   │   └── routes.py
│   │   ├── calendar/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── routes.py
│   │   ├── quiz/
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── routes.py
│   │   │   └── analytics.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── base.py
│   │   └── websocket/
│   │       ├── __init__.py
│   │       └── manager.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── app/
│   │   ├── app.json
│   │   ├── app.tsx
│   │   ├── package.json
│   │   ├── screens/
│   │   ├── components/
│   │   ├── navigation/
│   │   ├── store/
│   │   ├── services/
│   │   └── utils/
│   └── Dockerfile
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── USER_GUIDE.md
└── README.md
```

---

## 7. Development Roadmap

### Phase 1: MVP (Weeks 1-4)
- User authentication
- Subject/folder management
- Basic assignment creation
- Task breakdown algorithm
- Calendar view

### Phase 2: Scheduling & Notifications (Weeks 5-8)
- Scheduling engine
- Calendar conflict detection
- Push notifications
- Session tracking

### Phase 3: Spaced Repetition (Weeks 9-12)
- Spaced repetition scheduling
- Quiz & question system
- Retention scoring
- Analytics dashboard

### Phase 4: AI & Advanced Features (Weeks 13+)
- AI-powered task estimation
- Predictive workload analysis
- Natural language task input
- Mobile app refinement

---

## 8. Security Considerations

- **Authentication:** JWT tokens with 1h expiry + refresh tokens (7d)
- **Authorization:** Role-based access control (RBAC)
- **Data Encryption:** TLS 1.3 for transit, encryption at rest for sensitive data
- **Rate Limiting:** 100 requests/min per user
- **Input Validation:** Pydantic models with strict validation
- **CORS:** Whitelist approved domains
- **SQL Injection Prevention:** ORM + parameterized queries
- **Password Security:** bcrypt hashing with salt

---

## 9. Scalability & Performance

- **Database:** Connection pooling, read replicas, indexes on frequently queried columns
- **Caching:** Redis for session data, calendar events, user preferences
- **Task Queue:** Celery for async notifications, spaced repetition scheduling
- **Load Balancing:** Multiple FastAPI instances behind Nginx
- **CDN:** Static assets served via CloudFlare
- **Monitoring:** Prometheus metrics, Grafana dashboards, error tracking (Sentry)

---

## 10. Future Enhancements

- [ ] AI-powered task estimation using historical user data
- [ ] Integration with Google Calendar, Outlook, Canvas LMS
- [ ] Collaborative study groups with shared calendars
- [ ] Peer comparison & gamification
- [ ] Voice-based task input
- [ ] Computer vision for handwritten notes to OCR
- [ ] Parent/teacher dashboard for monitoring student progress
- [ ] ML model for predicting optimal study times
- [ ] Wearable integration (Apple Watch, Wear OS)
