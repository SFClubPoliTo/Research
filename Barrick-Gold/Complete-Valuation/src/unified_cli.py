"""Compatibility wrapper for the shared command line entry point."""
from main import ProjectLayout, UnifiedWorkflow, main
if __name__ == "__main__":
    raise SystemExit(main())
