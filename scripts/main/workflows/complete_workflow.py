"""Complete Instagram workflow: content generation + publishing."""

import asyncio
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from workflows.instagram_pipeline import run_complete_pipeline
from workflows.publishing_workflow import run_publishing_workflow

async def run_complete_instagram_workflow():
    """Run complete Instagram workflow: content generation + publishing."""
    print("🚀 Starting Complete Instagram Workflow")
    print("=" * 70)

    # Step 1: Generate content
    print("📝 STEP 1: Content Generation")
    print("-" * 30)

    content_success = await run_complete_pipeline()

    if not content_success:
        print("❌ Content generation failed. Aborting workflow.")
        return False

    print("\n✅ Content generation completed successfully!")
    print("=" * 70)

    # Step 2: Publish content
    print("📱 STEP 2: Publishing to Instagram")
    print("-" * 30)

    publishing_success = run_publishing_workflow()

    if not publishing_success:
        print("❌ Publishing failed.")
        return False

    print("\n✅ Publishing completed successfully!")
    print("=" * 70)
    print("🎉 COMPLETE INSTAGRAM WORKFLOW FINISHED!")
    print("🔗 Check your Instagram: @cryptoprism.io")
    print("=" * 70)

    return True

if __name__ == "__main__":
    """Main entry point for complete Instagram workflow."""
    success = asyncio.run(run_complete_instagram_workflow())

    if success:
        print("\n🎊 All operations completed successfully!")
        exit(0)
    else:
        print("\n💥 Workflow failed!")
        exit(1)