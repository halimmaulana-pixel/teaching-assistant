# Group Assignment Feature - Design Specification

## Overview

Add separate command for group project assignments (1 team leader + 4 members) alongside existing individual assignment system.

## Command

| Command | Purpose |
|---------|---------|
| `!create-assignment` | Individual assignment (existing) |
| `!create-group-assignment` | Group project assignment (new) |

## Thread Naming

| Type | Thread Name | Example |
|------|------------|---------|
| Individual | `tugas-{slug}` | `tugas-php-array` |
| Group | `tugas-kelompok-{slug}` | `tugas-kelompok-fullstack-web` |

## Submission Format

### Individual (existing)
```
NIM: [nim]
---
[assignment content]
```

### Group (new)
```
Nama Tim: [nama_tim]
Link Repo: [url]
Link Deploy: [url]
Job Desc: [project description - tech stack, database, framework, dll]
---
NIM: [nim_ketua] - Job Desc: [role]
NIM: [nim_2] - Job Desc: [role]
NIM: [nim_3] - Job Desc: [role]
NIM: [nim_4] - Job Desc: [role]
NIM: [nim_5] - Job Desc: [role]
```

## Thread Content Template (Group)

```
══════════════════════════════════════
📝 FORMAT SUBMISSION (WAJIB IKUTI):
══════════════════════════════════════
Nama Tim: [nama_tim]
Link Repo: [url]
Link Deploy: [url]
Job Desc: [project description - tech stack, database, framework, dll]
---
NIM: [nim_ketua] - Job Desc: [role]
NIM: [nim_2] - Job Desc: [role]
NIM: [nim_3] - Job Desc: [role]
NIM: [nim_4] - Job Desc: [role]
NIM: [nim_5] - Job Desc: [role]
══════════════════════════════════════
```

## Database Schema

### Group Submission (new table)
```python
{
    "id": "uuid",
    "assignment_id": "uuid",
    "team_name": "string",
    "repo_url": "string",
    "deploy_url": "string",
    "project_description": "string",
    "submitted_at": "datetime",
    "score": "integer (nullable)",
    "feedback": "string",
    "graded_by": "string",
    "graded_at": "datetime",
    "members": [
        {"nim": "xxx", "role": "Frontend Developer"},
        {"nim": "xxx", "role": "Backend Developer"},
        {"nim": "xxx", "role": "UI/UX Designer"},
        {"nim": "xxx", "role": "Database Admin"},
        {"nim": "xxx", "role": "DevOps"},
    ]
}
```

## Notification Flow

1. Student submit in thread
2. Bot extract all 5 NIMs + roles
3. Bot send DM to Dosen: new submission details
4. Bot post to `#grading-queue` channel: submission info + links
5. Dosen/AI review live web + repo
6. Dosen post grade → bot updates thread

## Grading Criteria (5 aspects)

| Criteria | Weight |
|----------|--------|
| Functional - Web accessible, features work | 20% |
| Code Quality - Clean code, proper structure | 20% |
| UI/UX - Attractive design, responsive | 20% |
| Deployment - Live link active and stable | 20% |
| Job Desc accuracy - Members roles match work | 20% |

## Command Parameters

`!create-group-assignment title:"..." desc:"..." deadline:"..." classes:"d1-si,c1-si"`

Same parameters as individual, just different command.

## Implementation Tasks

1. Add `handle_create_group_assignment` command
2. Add `format_group_thread_content` function
3. Add `parse_group_submission` function
4. Add `create_group_submission` database function
5. Update bot.py handler for new command
6. Add tests