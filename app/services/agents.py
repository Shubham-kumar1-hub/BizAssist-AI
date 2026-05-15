from dataclasses import dataclass

from app.services.llm import llm_service


@dataclass
class AgentResult:
    plan: str
    answer: str
    validation_notes: str


class PlannerAgent:
    def plan(self, user_message: str, context: str) -> str:
        prompt = f"""
User message:
{user_message}

Retrieved business context:
{context}

Create a short plan for answering the customer. Mention if a lead should be captured.
"""
        return llm_service.complete("You are a practical business assistant planner.", prompt)


class ExecutorAgent:
    def execute(self, user_message: str, context: str, memory: str, plan: str) -> str:
        prompt = f"""
Conversation memory:
{memory}

Retrieved knowledge:
{context}

Plan:
{plan}

Customer message:
{user_message}

Answer as a helpful SME business assistant. If the documents do not support an answer, say what is missing.
"""
        return llm_service.complete(
            "You answer business questions clearly, avoid unsupported claims, and ask for lead details when useful.",
            prompt,
        )


class ValidatorAgent:
    def validate(self, answer: str, context: str) -> str:
        prompt = f"""
Answer:
{answer}

Available context:
{context}

Check whether the answer is grounded and safe. Return one short validation note.
"""
        return llm_service.complete("You are a strict but concise AI answer validator.", prompt)


class AgentOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.validator = ValidatorAgent()

    def run(self, user_message: str, retrieved_docs: list[str], memory: str) -> AgentResult:
        context = "\n\n".join(retrieved_docs) if retrieved_docs else "No uploaded document context found."
        plan = self.planner.plan(user_message, context)
        answer = self.executor.execute(user_message, context, memory, plan)
        validation_notes = self.validator.validate(answer, context)
        return AgentResult(plan=plan, answer=answer, validation_notes=validation_notes)


agent_orchestrator = AgentOrchestrator()
