import uuid
import time
from datetime import datetime
from ..core.mimo_provider import MiMoProvider
from ..core.database import save_debate, update_leaderboard
from ..agents.personalities import ALL_AGENTS, JUDGE, AgentPersonality
from ..utils.logger import get_logger

logger = get_logger("engine")


class DebateEngine:
    def __init__(self):
        self.provider = MiMoProvider()
        self.debates: dict = {}

    async def start_debate(self, topic: str, num_rounds: int = 3, format_name: str = "free_form") -> dict:
        debate_id = str(uuid.uuid4())[:8]
        debate = {
            "id": debate_id,
            "topic": topic,
            "rounds": num_rounds,
            "format": format_name,
            "status": "running",
            "history": [],
            "started_at": datetime.utcnow().isoformat(),
            "agents": [a.name for a in ALL_AGENTS],
            "total_tokens_estimated": 0,
        }
        self.debates[debate_id] = debate
        logger.info(f"Debate started: {topic} ({debate_id})")

        for round_num in range(1, num_rounds + 1):
            logger.info(f"Round {round_num}/{num_rounds}")
            for agent in ALL_AGENTS:
                start = time.time()

                # Build personality-aware prompt
                prompt = agent.get_debate_prompt(topic, round_num, debate["history"])
                messages = [
                    {"role": "system", "content": agent.system_prompt},
                    {"role": "user", "content": prompt}
                ]

                response = await self.provider.chat(messages, temperature=0.8)
                elapsed = (time.time() - start) * 1000

                entry = {
                    "round": round_num,
                    "agent": agent.name,
                    "role": agent.role,
                    "content": response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "latency_ms": round(elapsed, 1),
                    "style": agent.style,
                }
                debate["history"].append(entry)
                debate["total_tokens_estimated"] += len(response.split()) * 1.3
                logger.info(f"{agent.name}: {len(response)} chars in {elapsed:.0f}ms")

        # Judge evaluation with Themis personality
        logger.info("Judge evaluating...")
        debate["judgment"] = await self._judge_evaluate(topic, debate["history"])
        debate["status"] = "completed"
        debate["completed_at"] = datetime.utcnow().isoformat()

        # Update leaderboard
        winner = debate["judgment"].get("winner", "")
        scores = debate["judgment"].get("scores", {})
        if scores:
            update_leaderboard(winner, scores)

        # Save to database
        save_debate(debate)

        logger.info(f"Winner: {winner}")
        return debate

    async def _judge_evaluate(self, topic: str, full_debate: list) -> dict:
        debate_text = "\n\n".join([f"**{h['agent']} (Round {h['round']})**: {h['content']}" for h in full_debate])
        messages = [
            {"role": "system", "content": JUDGE.system_prompt + """

Return evaluation as JSON:
{
    "winner": "agent_name",
    "reasoning": "detailed explanation of why they won (3-5 sentences)",
    "scores": {"Athena": 0-10, "Apollo": 0-10, "Atlas": 0-10},
    "key_arguments": ["best argument 1", "best argument 2", "best argument 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "round_analysis": {"1": "brief analysis", "2": "brief analysis", "3": "brief analysis"}
}"""},
            {"role": "user", "content": f"TOPIC: {topic}\n\nFULL DEBATE TRANSCRIPT:\n{debate_text}"}
        ]
        result = await self.provider.chat(messages, temperature=0.2)
        try:
            return json.loads(result.strip().strip("```json").strip("```"))
        except:
            return {"winner": ALL_AGENTS[0].name, "reasoning": result[:300], "scores": {a.name: 7 for a in ALL_AGENTS}, "key_arguments": [], "weaknesses": []}

    def get_debate(self, debate_id: str) -> dict:
        return self.debates.get(debate_id)

    def list_debates(self) -> list:
        return [{"id": d["id"], "topic": d["topic"], "status": d["status"], "winner": d.get("judgment",{}).get("winner")} for d in self.debates.values()]
