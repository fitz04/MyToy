"""Task planning and execution system."""
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import json


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    """Individual task in a plan."""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }


@dataclass
class Plan:
    """Execution plan containing multiple tasks."""
    id: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(
        self,
        task_id: str,
        description: str,
        dependencies: List[str] = None
    ) -> Task:
        """Add a task to the plan."""
        task = Task(
            id=task_id,
            description=description,
            dependencies=dependencies or []
        )
        self.tasks.append(task)
        self.updated_at = datetime.now()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_next_task(self) -> Optional[Task]:
        """Get next task that can be executed."""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                if self._dependencies_completed(task):
                    return task
        return None

    def _dependencies_completed(self, task: Task) -> bool:
        """Check if all task dependencies are completed."""
        for dep_id in task.dependencies:
            dep_task = self.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def get_progress(self) -> Dict[str, Any]:
        """Get plan execution progress."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": pending,
            "percentage": (completed / total * 100) if total > 0 else 0,
            "is_complete": completed == total,
            "has_failures": failed > 0
        }

    def to_dict(self) -> Dict:
        """Convert plan to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "progress": self.get_progress(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }

    def to_markdown(self) -> str:
        """Convert plan to markdown format."""
        progress = self.get_progress()

        md = f"# 📋 {self.description}\n\n"
        md += f"**Progress**: {progress['completed']}/{progress['total']} "
        md += f"({progress['percentage']:.1f}%)\n\n"

        md += "## Tasks\n\n"

        for i, task in enumerate(self.tasks, 1):
            # Status icon
            if task.status == TaskStatus.COMPLETED:
                icon = "✅"
            elif task.status == TaskStatus.IN_PROGRESS:
                icon = "🔄"
            elif task.status == TaskStatus.FAILED:
                icon = "❌"
            elif task.status == TaskStatus.SKIPPED:
                icon = "⏭️"
            else:
                icon = "⏳"

            md += f"{i}. {icon} **{task.description}**"

            if task.dependencies:
                md += f" (depends on: {', '.join(task.dependencies)})"

            md += "\n"

            if task.status == TaskStatus.IN_PROGRESS:
                if task.started_at:
                    elapsed = (datetime.now() - task.started_at).seconds
                    md += f"   - Started {elapsed}s ago\n"

            if task.status == TaskStatus.COMPLETED:
                if task.completed_at and task.started_at:
                    duration = (task.completed_at - task.started_at).seconds
                    md += f"   - Completed in {duration}s\n"

            if task.error:
                md += f"   - Error: {task.error}\n"

            md += "\n"

        return md


class TaskPlanner:
    """Task planning and execution manager."""

    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.current_plan: Optional[Plan] = None

    def create_plan(
        self,
        plan_id: str,
        description: str,
        tasks: List[Dict[str, Any]] = None
    ) -> Plan:
        """
        Create a new execution plan.

        Args:
            plan_id: Unique plan identifier
            description: Plan description
            tasks: Optional list of task definitions

        Returns:
            Created Plan object
        """
        plan = Plan(id=plan_id, description=description)

        if tasks:
            for task_def in tasks:
                plan.add_task(
                    task_id=task_def["id"],
                    description=task_def["description"],
                    dependencies=task_def.get("dependencies", [])
                )

        self.plans[plan_id] = plan
        self.current_plan = plan

        return plan

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get plan by ID."""
        return self.plans.get(plan_id)

    async def execute_task(
        self,
        task: Task,
        executor: Callable
    ) -> Dict[str, Any]:
        """
        Execute a single task.

        Args:
            task: Task to execute
            executor: Async function to execute the task

        Returns:
            Task execution result
        """
        try:
            # Mark as in progress
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()

            # Execute
            result = await executor(task)

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            return {
                "success": True,
                "task_id": task.id,
                "result": result
            }

        except Exception as e:
            # Mark as failed
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = str(e)

            return {
                "success": False,
                "task_id": task.id,
                "error": str(e)
            }

    async def execute_plan(
        self,
        plan: Plan,
        task_executor: Callable,
        on_task_start: Optional[Callable] = None,
        on_task_complete: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a plan sequentially.

        Args:
            plan: Plan to execute
            task_executor: Async function to execute each task
            on_task_start: Optional callback when task starts
            on_task_complete: Optional callback when task completes

        Returns:
            Plan execution result
        """
        results = []

        while True:
            # Get next task
            task = plan.get_next_task()
            if not task:
                break

            # Callback
            if on_task_start:
                await on_task_start(task)

            # Execute task
            result = await self.execute_task(task, task_executor)
            results.append(result)

            # Callback
            if on_task_complete:
                await on_task_complete(task, result)

            # Stop on failure if critical
            if not result["success"] and task.metadata.get("critical", False):
                break

        progress = plan.get_progress()

        return {
            "success": progress["is_complete"] and not progress["has_failures"],
            "plan_id": plan.id,
            "progress": progress,
            "results": results
        }

    def generate_plan_from_request(
        self,
        user_request: str,
        context: Dict[str, Any] = None
    ) -> Plan:
        """
        Generate a plan from a user request.

        This is a simplified version - in production, you'd use LLM to analyze
        the request and generate appropriate tasks.

        Args:
            user_request: User's request
            context: Optional context information

        Returns:
            Generated Plan
        """
        # Simple heuristic-based planning
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Analyze request
        request_lower = user_request.lower()

        tasks = []

        # Always start with analysis
        tasks.append({
            "id": "analyze",
            "description": "Analyze project structure and requirements",
            "dependencies": []
        })

        # Check for file operations
        if any(word in request_lower for word in ["create", "add", "new", "write"]):
            tasks.append({
                "id": "create_files",
                "description": "Create or modify necessary files",
                "dependencies": ["analyze"]
            })

        # Check for code generation
        if any(word in request_lower for word in ["implement", "code", "function", "class"]):
            tasks.append({
                "id": "generate_code",
                "description": "Generate code implementation",
                "dependencies": ["analyze"]
            })

        # Check for testing
        if "test" in request_lower or "verify" in request_lower:
            tasks.append({
                "id": "run_tests",
                "description": "Run tests and verify functionality",
                "dependencies": [t["id"] for t in tasks if t["id"] != "analyze"]
            })

        # Always end with commit
        tasks.append({
            "id": "git_commit",
            "description": "Commit changes to version control",
            "dependencies": [tasks[-1]["id"]]
        })

        return self.create_plan(
            plan_id=plan_id,
            description=f"Execute: {user_request}",
            tasks=tasks
        )

    def format_progress_bar(self, plan: Plan, width: int = 50) -> str:
        """
        Format a visual progress bar.

        Args:
            plan: Plan to visualize
            width: Width of progress bar

        Returns:
            Progress bar string
        """
        progress = plan.get_progress()
        percentage = progress["percentage"]

        filled = int(width * percentage / 100)
        empty = width - filled

        bar = "█" * filled + "░" * empty

        return f"[{bar}] {percentage:.1f}% ({progress['completed']}/{progress['total']})"


# Global instance
planner = TaskPlanner()
