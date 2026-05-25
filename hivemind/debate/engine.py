import uuid
import time
from datetime import datetime
from ..core.mimo_provider import MiMoProvider
from ..utils.logger import get_logger

logger = get_logger("engine")

AGENTS = [
    {"name": "Athena", "role": "Strategist", "style": "Logical, data-driven, systematic"},
    {"name": "Apollo", "role": "Innovator", "style": "Creative, contrarian, challenges assumptions"},
    {"name": "Atlas", "role": "Pragmatist", "style": "Practical, real-world focused, risk-aware"},
]


class DebateEngine:
    def __init__(self):
        self.provider = MiMoProvider()
        self.debates: dict = {}

    async def start_debate(self, topic: str, num_rounds: int = 3) -> dict:
        debate_id = str(uuid.uuid4())[:8]
        debate = {
            "id": debate_id,
            "topic": topic,
            "rounds": num_rounds,
            "status": "running",
            "history": [],
            "started_at": datetime.utcnow().isoformat(),
            "agents": [a["name"] for a in AGENTS],
            "total_tokens_estimated": 0,
        }
        self.debates[debate_id] = debate
        logger.info(f"Debate started: {topic} ({debate_id})")

        for round_num in range(num_rounds):
            logger.info(f"Round {round_num + 1}/{num_rounds}")
            for agent in AGENTS:
                start = time.time()
                position = f"Round {round_num + 1} argument"
                response = await self.provider.debate_respond(
                    agent["name"], topic, debate["history"], position
                )
                elapsed = (time.time() - start) * 1000

                entry = {
                    "round": round_num + 1,
                    "agent": agent["name"],
                    "role": agent["role"],
                    "content": response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "latency_ms": round(elapsed, 1),
                }
                debate["history"].append(entry)
                debate["total_tokens_estimated"] += len(response.split()) * 1.3
                logger.info(f"{agent['name']}: {len(response)} chars in {elapsed:.0f}ms")

        # Judge evaluation
        logger.info("Judge evaluating...")
        debate["judgment"] = await self.provider.judge_evaluate(topic, debate["history"])
        debate["status"] = "completed"
        debate["completed_at"] = datetime.utcnow().isoformat()
        logger.info(f"Winner: {debate['judgment'].get('winner', 'N/A')}")

        return debate

    def get_debate(self, debate_id: str) -> dict:
        return self.debates.get(debate_id)

    def list_debates(self) -> list:
        return [{"id": d["id"], "topic": d["topic"], "status": d["status"], "winner": d.get("judgment",{}).get("winner")} for d in self.debates.values()]
