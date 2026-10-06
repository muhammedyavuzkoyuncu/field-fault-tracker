
# Project Decisions

This document records the main technical and architectural decisions made during the development of the Field Fault Tracker project.

The purpose of this document is to keep track of why specific technologies, structures, and approaches were selected.

---

## Decision 1 - Backend Framework

### Decision

Python FastAPI was selected as the backend framework.

### Reason

FastAPI provides:

- REST API support
- Automatic API documentation
- Pydantic-based request validation
- Good integration with Python
- Suitable performance for the project
- Easy integration with SQL databases

The backend is responsible for communication between the mobile/web clients and the PostgreSQL database.

---

## Decision 2 - Database

### Decision

PostgreSQL was selected as the relational database system.

### Reason

The project contains structured and relational data such as:

- Plants
- Equipment
- Technicians
- Fault categories
- Fault records

PostgreSQL provides foreign key relationships, constraints, transactions, and reliable relational data management.

---

## Decision 3 - Local Database Environment

### Decision

PostgreSQL is used through Docker during local development.

### Reason

Using Docker provides a consistent and isolated database environment.

The local database configuration is:

```text
Database: saha_ariza
User: admin
Port: 5432
Container: saha_ariza_postgres

The local database is used for development and testing.

Decision 4 - Production Database
Decision

Neon PostgreSQL was selected for the production database.

Reason

The backend is deployed on Render and requires an externally accessible PostgreSQL database.

Neon provides a managed PostgreSQL environment that can be connected to the deployed FastAPI application.

The production database is separated from the local Docker database.

Decision 5 - Database Migration Tool
Decision

Alembic was selected for database schema migrations.

Reason

Alembic provides version-controlled database schema changes and integrates well with SQLAlchemy.

It allows database changes to be tracked and reproduced between development and production environments.

Decision 6 - Database Naming Convention
Decision

English table names were selected for the final database schema.

Initial Structure

The initial database used Turkish table names:

santraller
ekipmanlar
teknikerler
ariza_kategorileri
arizalar
Final Structure

The final database uses:

plants
equipment
technicians
fault_categories
faults
Reason

English naming provides a consistent naming convention across:

Backend code
Database tables
API endpoints
Documentation
Future mobile application
Decision 7 - Data Migration Strategy
Decision

Existing local data was preserved and transferred to the new English database structure.

Reason

The existing data was required for development and testing.

Instead of recreating the data manually, the migration process transferred the existing records while changing the database structure.

The production Neon database was later populated with the development data.

Decision 8 - API Architecture
Decision

The backend exposes REST-style HTTP endpoints.

Reason

A REST API provides a common communication layer for different clients.

The same backend can therefore be used by:

Web Management Interface
          |
          v
      FastAPI API
          ^
          |
Flutter Mobile Application

This architecture avoids duplicating business logic between clients.

Decision 9 - Fault CRUD Operations
Decision

Fault records support Create, Read, Update, and Delete operations.

Implemented Operations
POST   /faults
GET    /faults
GET    /faults/{fault_id}
PUT    /faults/{fault_id}
DELETE /faults/{fault_id}
Reason

Fault management requires the ability to create new records and manage existing records throughout their lifecycle.

Decision 10 - Fault Status
Decision

Fault records contain a status field.

The current API supports status values such as:

ACIK
DEVAM_EDIYOR

Additional status values can be introduced as the business requirements become clearer.

Reason

A fault is not only a static record. Its progress needs to be tracked from creation to resolution.

Decision 11 - Fault Priority
Decision

Fault records contain a priority field.

The current default priority is:

ORTA

The API also supports other priority values such as:

YUKSEK
Reason

Different faults may have different levels of operational importance.

A priority field allows the management interface to distinguish between faults with different urgency levels.

Decision 12 - Equipment Relationship
Decision

Each fault can be associated with an equipment record.

The relationship is implemented using:

faults.equipment_id
        |
        v
equipment.id
Reason

A fault needs to identify which equipment is affected.

This relationship also allows the management interface to display plant and equipment information together with the fault.

Decision 13 - Technician Relationship
Decision

Each fault can be associated with a technician.

The relationship is implemented using:

faults.technician_id
        |
        v
technicians.id
Reason

Technician information is required for assigning and tracking responsibility for field operations.

Decision 14 - Fault Category Relationship
Decision

Each fault can be associated with a fault category.

The relationship is implemented using:

faults.category_id
        |
        v
fault_categories.id
Reason

Categorizing faults makes it possible to organize and analyze fault records according to their type.

Decision 15 - Client UUID
Decision

A client_uuid field is included in the fault table.

Reason

The future mobile application is planned to support offline operation.

A locally generated UUID can identify a fault before it reaches the central database.

This can help with future synchronization and duplicate detection mechanisms.

Decision 16 - Mobile Application
Decision

Flutter was selected for the mobile application.

Reason

Flutter allows a single codebase to be used for mobile application development.

The planned mobile application will communicate with the FastAPI backend.

The application is intended to support field technicians working in environments where network connectivity may be limited.

Decision 17 - Offline Capability
Decision

Offline operation is included as a future requirement.

Reason

Field technicians may work in areas where network connectivity is unavailable or unstable.

The planned architecture therefore allows fault records to be created locally and synchronized with the central backend when connectivity becomes available.

The exact synchronization strategy will be implemented during the mobile application development phase.

Decision 18 - API Testing
Decision

Postman is used for API testing during backend development.

Reason

Postman allows endpoints to be tested independently from the future mobile and web clients.

This makes it possible to verify:

Request formats
Response formats
HTTP methods
CRUD operations
Error cases
Database integration

before client development is completed.

Decision 19 - Deployment
Decision

Render was selected for backend deployment.

Reason

The FastAPI application needs to be accessible remotely by future clients.

Render provides a deployment environment for running the FastAPI backend and connecting it to the Neon PostgreSQL database.

The production architecture is:

Client
  |
  v
Render
  |
  v
FastAPI
  |
  v
Neon PostgreSQL
Decision 20 - Development Strategy
Decision

The project is being developed incrementally.

Development Order

The planned order is:

Project Planning
       |
       v
Database Design
       |
       v
Backend Development
       |
       v
Database Migration
       |
       v
Production Database
       |
       v
API Testing
       |
       v
Web Management Interface
       |
       v
Flutter Mobile Application
       |
       v
Offline Synchronization
       |
       v
Final Integration Testing
Reason

Developing the backend and database before the client applications provides a stable API foundation for both the web and mobile applications.
Decision 21 - Separation of Environments
Decision

Local development and production environments are kept separate.

Local Environment
FastAPI
   |
   v
Docker PostgreSQL
Production Environment
FastAPI on Render
        |
        v
Neon PostgreSQL
Reason

Separating the environments prevents development and testing operations from directly affecting production data.

Decision 22 - Documentation
Decision

Project decisions and technical information are documented in Markdown files.

The main documentation files are:

README.md
DECISIONS.md
Reason

Keeping technical decisions documented makes the project easier to understand, maintain, and continue in future development stages.

Decision 23 - Web Management Interface
Decision

A separate web management interface will be developed for central users.

Planned Responsibilities

The web interface will provide:

Fault dashboard
Fault listing
Fault details
Fault filtering
Fault updating
Fault deletion
Equipment information
Technician information
Fault category information
Reason

Central management requires a visual interface for monitoring and managing field fault records.

The web interface will use the existing FastAPI backend rather than directly accessing the database.

Decision 24 - Client and Database Separation
Decision

Client applications will not connect directly to PostgreSQL.

The intended architecture is:

Web / Flutter
      |
      v
 FastAPI API
      |
      v
 PostgreSQL
Reason

Keeping database access inside the backend provides a controlled API layer and prevents client applications from directly accessing database credentials or database operations.

Decision 25 - Current Development Status

The following components have been completed:

Project planning
Database design
Local PostgreSQL setup
SQLAlchemy database integration
Alembic migration setup
English database schema
FastAPI backend
Fault CRUD operations
Neon PostgreSQL setup
Production data migration
Render deployment
API testing

The following components remain:

Web management interface
Flutter mobile application
Offline synchronization
Final integration testing
Conclusion

The decisions documented above establish the current technical foundation of the Field Fault Tracker project.

The architecture is designed to support both a central web management interface and a Flutter-based field application while maintaining a centralized FastAPI and PostgreSQL backend.