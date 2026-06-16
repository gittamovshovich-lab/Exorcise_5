#!/usr/bin/env python3
"""
מערכת יצירת מאמרים מקצועיים - Professional Article Creation System
Multi-Agent Orchestration using CrewAI

Pipeline:
    1. Research Agent  → אוסף מידע מהאינטרנט
    2. Writer Agent    → כותב מאמר על בסיס המחקר
    3. Editor Agent    → משפר ומתקן את המאמר
    4. Publisher Agent → מפיק תוצר סופי מוכן לפרסום

Usage:
    python main.py
    python main.py --topic "Your custom topic here"
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Load API keys from .env file
load_dotenv()

# =============================================================================
# TOOL INITIALIZATION
# =============================================================================

# Web search tool — requires SERPER_API_KEY in .env
search_tool = SerperDevTool()

# =============================================================================
# AGENT DEFINITIONS
# Each agent has: role, goal, backstory (system prompt), and tools
# =============================================================================

# --- Agent 1: Research Agent ---
# First in the pipeline — searches the web and organizes a research brief
research_agent = Agent(
    role="Senior Research Analyst",
    goal=(
        "Collect comprehensive, accurate, and relevant information on the given topic. "
        "Identify key facts, statistics, expert opinions, and current trends."
    ),
    backstory=(
        "You are a seasoned research analyst with over 15 years of experience in academic "
        "and professional research. Your methodology is rigorous: you verify facts from "
        "multiple credible sources, prioritize authoritative and peer-reviewed content, "
        "and organize findings in a structured, logical manner. You always provide context "
        "for the data you collect and highlight the most significant discoveries. "
        "You never fabricate information — every fact you report is grounded in real evidence. "
        "Your research briefs are legendary for their clarity and completeness, forming the "
        "foundation upon which excellent articles are built."
    ),
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
)

# --- Agent 2: Writer Agent ---
# Receives research brief and transforms it into a full article
writer_agent = Agent(
    role="Professional Content Writer",
    goal=(
        "Transform research findings into a compelling, well-structured professional article "
        "that engages readers while maintaining intellectual rigor and accuracy."
    ),
    backstory=(
        "You are an award-winning content writer with a decade of experience crafting "
        "professional articles for leading publications, technology companies, and academic journals. "
        "You have mastered the art of translating complex research into accessible, engaging prose. "
        "Your writing philosophy centers on three pillars: clarity, credibility, and compelling narrative. "
        "You structure every article with a powerful introduction that hooks the reader, "
        "a logically flowing body that presents arguments progressively with evidence, "
        "and a conclusion that synthesizes insights and leaves readers with actionable takeaways. "
        "You write exclusively from the research provided — never inventing facts — "
        "and you adapt your style to a professional audience that values depth and precision."
    ),
    tools=[],
    verbose=True,
    allow_delegation=False,
)

# --- Agent 3: Editor Agent ---
# Reviews the draft article and improves quality across all dimensions
editor_agent = Agent(
    role="Senior Content Editor",
    goal=(
        "Refine, improve, and polish the article to meet the highest professional standards "
        "by correcting errors, improving flow, enhancing clarity, and strengthening arguments."
    ),
    backstory=(
        "You are a meticulous senior editor with 20 years of experience at major publishing "
        "houses and leading digital media companies. You have edited thousands of articles and "
        "developed an unparalleled eye for quality. Your editing process follows a strict order: "
        "first you check factual accuracy and logical consistency, then you address structural issues, "
        "followed by sentence-level improvements for clarity and flow, and finally you catch "
        "grammatical, punctuation, and stylistic errors. You believe that great editing is invisible — "
        "the final article should read as if it was written perfectly from the start. "
        "You make substantive improvements while always preserving the author's voice and intent. "
        "You return the fully improved article, not just a list of corrections."
    ),
    tools=[],
    verbose=True,
    allow_delegation=False,
)

# --- Agent 4: Publisher Agent ---
# Formats the final article into publication-ready markdown with metadata
publisher_agent = Agent(
    role="Content Publisher and Formatter",
    goal=(
        "Format and present the final article in a professional, publication-ready format "
        "with proper markdown structure, SEO metadata, and reader-friendly layout."
    ),
    backstory=(
        "You are an experienced content publisher with 15 years in digital and print media. "
        "You understand that presentation is as important as content — proper formatting "
        "dramatically increases readability and engagement. You specialize in markdown formatting, "
        "SEO optimization, and content structuring for maximum impact across platforms. "
        "Your publication checklist includes: crafting an SEO-optimized title, writing a compelling "
        "meta description (150-160 characters), structuring headings in H1/H2/H3 hierarchy, "
        "creating an executive summary, calculating estimated reading time, adding relevant tags, "
        "and appending a strong call to action. Your output is always a complete, polished "
        "document ready for immediate publication on any modern content platform."
    ),
    tools=[],
    verbose=True,
    allow_delegation=False,
)

# =============================================================================
# TASK DEFINITIONS
# Tasks define WHAT each agent must do, the expected output, and context flow
# =============================================================================

def create_tasks(topic: str) -> list:
    """
    Build the four sequential tasks for the article creation pipeline.

    Args:
        topic: The subject of the article to be created.

    Returns:
        List of Task objects in pipeline order.
    """

    # --- Task 1: Research ---
    research_task = Task(
        description=(
            f"Conduct comprehensive research on the topic: '{topic}'.\n\n"
            "Your research MUST include all of the following:\n"
            "1. Key facts, statistics, and verified data points\n"
            "2. Current trends and the most recent developments (last 1-2 years)\n"
            "3. Expert opinions and quotes from credible, authoritative sources\n"
            "4. Real-world examples and relevant case studies\n"
            "5. Multiple perspectives and any ongoing debates in the field\n\n"
            "Organize all findings into a structured research brief with clearly labeled sections. "
            "This brief will be handed directly to a professional writer, so make it thorough and well-organized."
        ),
        expected_output=(
            "A comprehensive research brief (500-700 words) organized into these sections:\n"
            "## Executive Summary\n"
            "3-5 bullet points of the most critical findings.\n\n"
            "## Background & Context\n"
            "Historical or foundational information about the topic.\n\n"
            "## Current State & Trends\n"
            "Latest developments, statistics, and data points.\n\n"
            "## Expert Opinions\n"
            "Insights, quotes, or positions from credible experts.\n\n"
            "## Key Insights for the Article\n"
            "The most important takeaways the article should highlight.\n\n"
            "## Sources Consulted\n"
            "List of sources used."
        ),
        agent=research_agent,
    )

    # --- Task 2: Writing ---
    # context=[research_task] means this task receives the output of Task 1
    writing_task = Task(
        description=(
            f"Using ONLY the research brief provided in your context, write a professional "
            f"article about '{topic}'.\n\n"
            "The article MUST follow this structure and guidelines:\n"
            "1. TITLE: A compelling, informative title\n"
            "2. INTRODUCTION (100-150 words): Open with a hook, establish why this topic matters, "
            "   and state a clear thesis.\n"
            "3. BODY (3-4 sections, 150-200 words each): Each section should have a subheading "
            "   and develop one main argument supported by evidence from the research.\n"
            "4. CONCLUSION (100-150 words): Synthesize the key insights and leave the reader "
            "   with meaningful takeaways.\n\n"
            "IMPORTANT: Every factual claim must come from the research brief. "
            "Do NOT invent statistics or quotes. Write for a professional audience."
        ),
        expected_output=(
            "A complete, well-structured article (800-1000 words) containing:\n"
            "- An engaging, descriptive title\n"
            "- Introduction with clear thesis (100-150 words)\n"
            "- 3-4 body sections with descriptive subheadings (150-200 words each)\n"
            "- Conclusion with actionable insights (100-150 words)\n"
            "- Professional, engaging tone consistent throughout"
        ),
        agent=writer_agent,
        context=[research_task],  # Passes research brief as context
    )

    # --- Task 3: Editing ---
    # context=[writing_task] means this task receives the draft article from Task 2
    editing_task = Task(
        description=(
            "You have received a draft article. Edit it thoroughly following this process:\n\n"
            "STEP 1 - ACCURACY CHECK: Verify all claims are internally consistent and grounded.\n"
            "STEP 2 - STRUCTURE REVIEW: Ensure the article has logical flow and clear progression. "
            "         Reorder sections or paragraphs if needed.\n"
            "STEP 3 - CLARITY IMPROVEMENTS: Simplify overly complex sentences. Eliminate "
            "         unnecessary jargon. Ensure each paragraph has one clear idea.\n"
            "STEP 4 - STYLE ENHANCEMENT: Improve word choice, vary sentence length for rhythm, "
            "         strengthen weak verbs, and sharpen the opening and closing lines.\n"
            "STEP 5 - GRAMMAR & MECHANICS: Correct all grammatical, punctuation, and spelling errors.\n"
            "STEP 6 - CONSISTENCY: Ensure consistent tone, terminology, and formatting throughout.\n\n"
            "Return the FULL edited article — do not return only corrections or comments."
        ),
        expected_output=(
            "The fully edited and polished article that:\n"
            "- Is completely free of grammatical and stylistic errors\n"
            "- Has demonstrably improved clarity and flow compared to the draft\n"
            "- Maintains a consistent, professional tone throughout\n"
            "- Has been tightened for conciseness without losing substance\n"
            "- Includes a brief Editor's Note at the top (2-3 sentences) describing "
            "  the key improvements made and why"
        ),
        agent=editor_agent,
        context=[writing_task],  # Passes draft article as context
    )

    # --- Task 4: Publishing ---
    # context=[editing_task] means this task receives the polished article from Task 3
    publishing_task = Task(
        description=(
            "You have received the final edited article. Prepare it for publication by "
            "adding all required metadata and formatting:\n\n"
            "1. PUBLICATION METADATA BLOCK: Include title, date (today's date), "
            "   estimated reading time (calculate from word count at 200 wpm), "
            "   author placeholder, and category.\n"
            "2. SEO META DESCRIPTION: Write a 150-160 character description for search engines.\n"
            "3. TAGS: Suggest 5-7 relevant topic tags.\n"
            "4. EXECUTIVE SUMMARY: A 50-word summary for readers who skim.\n"
            "5. MARKDOWN FORMATTING: Apply full markdown — H1 for title, H2 for main sections, "
            "   H3 for subsections, **bold** for key terms, *italic* for emphasis.\n"
            "6. CALL TO ACTION: Add a professional closing CTA inviting engagement.\n"
            "7. RELATED TOPICS: Suggest 3-5 related topics for further reading.\n\n"
            "The output must be a complete, copy-paste-ready markdown document."
        ),
        expected_output=(
            "A complete, publication-ready markdown document containing:\n"
            "- A frontmatter metadata block (title, date, reading time, author, tags, description)\n"
            "- Executive summary section\n"
            "- Fully formatted article body with H1/H2/H3 hierarchy and markdown styling\n"
            "- Call to action section\n"
            "- Related topics section\n"
            "All formatted as valid markdown, ready for direct publication."
        ),
        agent=publisher_agent,
        context=[editing_task],  # Passes polished article as context
    )

    return [research_task, writing_task, editing_task, publishing_task]


# =============================================================================
# CREW ASSEMBLY AND EXECUTION
# =============================================================================

def run_article_creation_system(topic: str) -> str:
    """
    Assemble the Multi-Agent Crew and run the article creation pipeline.

    Args:
        topic: The subject of the article to be created.

    Returns:
        The final publication-ready article as a string.
    """
    print("\n" + "=" * 70)
    print("  PROFESSIONAL ARTICLE CREATION SYSTEM - CrewAI Multi-Agent")
    print("=" * 70)
    print(f"  Topic   : {topic}")
    print(f"  Agents  : Research → Writer → Editor → Publisher")
    print(f"  Process : Sequential Pipeline")
    print("=" * 70 + "\n")

    # Build the four sequential tasks
    tasks = create_tasks(topic)

    # Assemble the Crew — sequential process ensures agents run in order
    article_crew = Crew(
        agents=[research_agent, writer_agent, editor_agent, publisher_agent],
        tasks=tasks,
        process=Process.sequential,  # Each agent waits for the previous to finish
        verbose=True,                 # Prints full agent reasoning to console
    )

    # Execute the pipeline — each task's output feeds into the next via context
    result = article_crew.kickoff()

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE — Article successfully created!")
    print("=" * 70 + "\n")

    return result


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Professional Article Creation System using CrewAI Multi-Agent Orchestration"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="The Impact of Artificial Intelligence on Modern Healthcare",
        help="Topic for the article to generate (default: AI in Healthcare)",
    )
    args = parser.parse_args()

    # Run the multi-agent pipeline
    final_article = run_article_creation_system(args.topic)

    # Save the result to a markdown file
    output_path = "output_article.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(final_article))

    print(f"Article saved to: {output_path}\n")
