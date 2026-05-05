from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

SKILLS_DIR = Path(__file__).parent / "skills"

mcp = FastMCP("Skills Server")
mcp.add_provider(
    SkillsDirectoryProvider(
        roots=SKILLS_DIR,
        supporting_files="resources",
        reload=True,
    )
)


@mcp.tool(description="List all available skills by name and description")
def list_skills() -> list[dict]:
    """Returns a list of all skills with their name and description."""
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_dir.is_dir() and skill_file.exists():
            content = skill_file.read_text(encoding="utf-8")
            # Extract description from frontmatter if present
            description = ""
            lines = content.splitlines()
            in_frontmatter = False
            for line in lines:
                if line.strip() == "---":
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter and line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()
                    break
            skills.append({"name": skill_dir.name, "description": description})
    return skills


@mcp.tool(description="Get the full SKILL.md content for a specific skill by name")
def get_skill(name: str) -> str:
    """Returns the full SKILL.md content for the given skill name."""
    skill_file = SKILLS_DIR / name / "SKILL.md"
    if not skill_file.exists():
        available = [d.name for d in SKILLS_DIR.iterdir() if d.is_dir()]
        return f"Skill '{name}' not found. Available skills: {', '.join(available)}"
    return skill_file.read_text(encoding="utf-8")
