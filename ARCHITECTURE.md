# Proposed .NET Microservices & APIs

## Identity Service
Handles registration, login, JWT token issuance, and user profile.
- `POST /api/auth/register` – create user account and return JWT
- `POST /api/auth/login` – authenticate and return JWT
- `GET /api/users/{id}` – retrieve user profile
- `PUT /api/users/{id}` – update profile or preferences

## Assessment Service
Manages mental‑health assessments such as DASS‑21 and PHQ‑9.
- `POST /api/assessments/dass21` – submit responses and return scores/analysis
- `POST /api/assessments/phq9` – submit responses and return scores/analysis
- `GET /api/assessments/history/{userId}` – list past results

## Tracker Service
Logs daily metrics (mood, sleep, etc.) and generates summaries.
- `POST /api/trackers` – add a log entry
- `GET /api/trackers/{userId}` – retrieve logs (with optional date filters)
- `GET /api/trackers/{userId}/summary` – aggregated statistics

## Gamification Service
Awards XP and badges, mirroring existing gamification utilities.
- `POST /api/gamification/award` – grant XP/badges to a user
- `GET /api/gamification/{userId}` – fetch level, XP, badges

## Journey Service
Delivers guided “journeys” (sets of tasks or lessons) and tracks progress.
- `POST /api/journeys` – create a journey
- `GET /api/journeys` – list available journeys
- `POST /api/journeys/{journeyId}/start` – enroll user
- `PUT /api/journeys/{journeyId}/steps/{stepId}` – mark step complete

## NLP Analysis Service
Wraps external NLP providers for sentiment or text analysis.
- `POST /api/nlp/analyze` – submit text and return sentiment/results

## API Gateway
Optional façade routing external traffic to individual services and aggregating Swagger documentation.

_All services should enable Swagger (`builder.Services.AddEndpointsApiExplorer(); builder.Services.AddSwaggerGen();`) so endpoints are documented and testable._

---

# SQL Server Table Design

```sql
CREATE TABLE Users (
    UserId UNIQUEIDENTIFIER PRIMARY KEY,
    Email NVARCHAR(256) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(256) NOT NULL,
    FullName NVARCHAR(100),
    Age INT,
    StudentLevel NVARCHAR(50),
    ConsentGiven BIT NOT NULL,
    Xp INT DEFAULT 0,
    Level INT DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE Dass21Results (
    ResultId UNIQUEIDENTIFIER PRIMARY KEY,
    UserId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    DepressionScore INT,
    AnxietyScore INT,
    StressScore INT,
    DepressionLevel NVARCHAR(20),
    AnxietyLevel NVARCHAR(20),
    StressLevel NVARCHAR(20),
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE Phq9Results (
    ResultId UNIQUEIDENTIFIER PRIMARY KEY,
    UserId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    TotalScore INT,
    SeverityLevel NVARCHAR(20),
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE TrackerEntries (
    EntryId UNIQUEIDENTIFIER PRIMARY KEY,
    UserId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    TrackerType NVARCHAR(50),
    TrackerValue NVARCHAR(100),
    EntryDate DATETIME2 NOT NULL
);

CREATE TABLE Badges (
    BadgeId INT IDENTITY PRIMARY KEY,
    Name NVARCHAR(100) NOT NULL,
    Description NVARCHAR(255)
);

CREATE TABLE UserBadges (
    UserId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    BadgeId INT NOT NULL FOREIGN KEY REFERENCES Badges(BadgeId),
    EarnedAt DATETIME2 NOT NULL,
    PRIMARY KEY (UserId, BadgeId)
);

CREATE TABLE Journeys (
    JourneyId UNIQUEIDENTIFIER PRIMARY KEY,
    Title NVARCHAR(100),
    Description NVARCHAR(255)
);

CREATE TABLE JourneySteps (
    StepId UNIQUEIDENTIFIER PRIMARY KEY,
    JourneyId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Journeys(JourneyId),
    StepOrder INT NOT NULL,
    Content NVARCHAR(MAX)
);

CREATE TABLE UserJourneyProgress (
    UserId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Users(UserId),
    JourneyId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES Journeys(JourneyId),
    StepId UNIQUEIDENTIFIER NOT NULL FOREIGN KEY REFERENCES JourneySteps(StepId),
    Completed BIT NOT NULL,
    CompletedAt DATETIME2,
    PRIMARY KEY (UserId, StepId)
);
```

Each microservice can maintain its own context and migration set; they can share the same SQL Server or separate databases, depending on deployment strategy.

---

# EF Core Migration Workflow

1. Define entity classes matching the table schemas.
2. In each microservice:
   ```bash
   dotnet ef migrations add InitialCreate
   dotnet ef database update
   ```
3. Migrations will create the tables in SQL Server; verify in SQL Server Management Studio (SSMS).

---

# DevOps Considerations

- **CI/CD**: Use GitHub Actions or Azure DevOps pipelines to build each microservice, run tests, execute `dotnet ef database update`, and publish Docker images.
- **Containerization**: Package each service with its own Dockerfile; deploy with Docker Compose or Kubernetes.
- **Monitoring & Logging**: Integrate Serilog or Application Insights for centralized logging and metrics.
- **API Documentation**: Aggregate Swagger JSON from all services at the gateway for a unified API portal.
