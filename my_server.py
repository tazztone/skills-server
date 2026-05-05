from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP("Skills Server")
mcp.add_provider(
    SkillsDirectoryProvider(
        roots=Path(__file__).parent / "skills",
        supporting_files="resources",
        reload=True,
    )
)
