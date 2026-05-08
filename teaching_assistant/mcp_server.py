"""MCP server for AI grading integration."""
import logging
from mcp.server import Server
from mcp.types import Tool, TextContent

logger = logging.getLogger("teaching-assistant")

server = Server("teaching-assistant-grading")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List grading tools available to AI."""
    return [
        Tool(
            name="get_pending_submissions",
            description="Get all submissions that need grading",
            inputSchema={
                "type": "object",
                "properties": {
                    "assignment_id": {"type": "string", "description": "Assignment ID to filter by"}
                }
            }
        ),
        Tool(
            name="get_submission_content",
            description="Get the full content of a submission for grading",
            inputSchema={
                "type": "object",
                "properties": {
                    "submission_id": {"type": "string", "description": "The submission ID"}
                },
                "required": ["submission_id"]
            }
        ),
        Tool(
            name="submit_grade",
            description="Submit the grading result for a submission",
            inputSchema={
                "type": "object",
                "properties": {
                    "submission_id": {"type": "string"},
                    "score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "feedback": {"type": "string"},
                    "strengths": {"type": "array", "items": {"type": "string"}},
                    "improvements": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["submission_id", "score", "feedback"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from AI."""
    if name == "get_pending_submissions":
        return await get_pending_submissions(arguments.get("assignment_id"))
    elif name == "get_submission_content":
        return await get_submission_content(arguments["submission_id"])
    elif name == "submit_grade":
        return await submit_grade(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def get_pending_submissions(assignment_id: str = None) -> list[TextContent]:
    """Get submissions pending grading."""
    from teaching_assistant.services.database import get_pending_submissions

    submissions = await get_pending_submissions(assignment_id)

    if not submissions:
        return [TextContent(type="text", text="No pending submissions")]

    result = "📋 Pending Submissions:\n\n"
    for sub in submissions:
        result += f"- ID: {sub['id']}\n"
        result += f"  NIM: {sub['nim']}\n"
        result += f"  Content: {sub['content'][:100]}...\n"
        result += f"  Attachments: {len(sub['attachments'])}\n\n"

    return [TextContent(type="text", text=result)]

async def get_submission_content(submission_id: str) -> list[TextContent]:
    """Get full submission content for grading."""
    from teaching_assistant.services.database import get_submission

    submission = await get_submission(submission_id)

    if not submission:
        return [TextContent(type="text", text=f"Submission not found: {submission_id}")]

    result = f"## Submission: {submission_id}\n\n"
    result += f"**NIM:** {submission['nim']}\n"
    result += f"**Student:** {submission['student_name']}\n"
    result += f"**Class:** {submission['class_channel']}\n"
    result += f"**Submitted:** {submission['submitted_at']}\n\n"
    result += f"## Content:\n{submission['content']}\n\n"

    if submission['attachments']:
        result += "## Attachments:\n"
        for att in submission['attachments']:
            result += f"- {att['filename']}: {att['url']}\n"

    return [TextContent(type="text", text=result)]

async def submit_grade(arguments: dict) -> list[TextContent]:
    """Submit grading result."""
    from teaching_assistant.services.database import update_submission_grade

    await update_submission_grade(
        submission_id=arguments["submission_id"],
        score=arguments["score"],
        feedback=arguments["feedback"],
        strengths=arguments.get("strengths", []),
        improvements=arguments.get("improvements", []),
        graded_by="Claude AI"
    )

    logger.info(f"Grade submitted for {arguments['submission_id']}: {arguments['score']}/100")

    return [TextContent(type="text", text=f"✅ Grade submitted: {arguments['score']}/100")]