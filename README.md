# Instructions

You are developing an inventory management software solution for a cloud services company that provisions servers in multiple data centers. You must build a CRUD app for tracking the state of all the servers. 

Deliverables:
- PR to https://github.com/Mathpix/hiring-challenge-devops-python that includes:
- API code
- CLI code
- pytest test suite
- Working Docker Compose stack

Short API.md on how to run everything, also a short API and CLI spec

Required endpoints:
- POST /servers → create a server
- GET /servers → list all servers
- GET /servers/{id} → get one server
- PUT /servers/{id} → update server
- DELETE /servers/{id} → delete server

Requirements:
- Use FastAPI or Flask
- Store data in PostgreSQL
- Use raw SQL

Validate that:
- hostname is unique
- IP address looks like an IP

State is one of: active, offline, retired

