import httpx, json
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger("mimo")

class MiMoProvider:
    def __init__(self):
        self.config = Config()

    async def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        url = f"{self.config.MIMO_BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {self.config.MIMO_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": self.config.MIMO_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def debate_respond(self, agent_role: str, topic: str, history: list, position: str) -> str:
        system = f"""You are {agent_role} in a structured debate.
TOPIC: {topic}
YOUR POSITION: {position}
Rules:
- Present strong arguments with evidence
- Counter opponents points directly
- Be persuasive but factual
- Keep responses under 300 words
- Use data and examples when possible"""
        messages = [{"role": "system", "content": system}]
        for h in history:
            messages.append({"role": "user" if h["role"] != agent_role else "assistant", "content": f'{h["role"]}: {h["content"]}'})
        messages.append({"role": "user", "content": f"Continue the debate. Make your next argument."})
        return await self.chat(messages)

    async def judge_evaluate(self, topic: str, full_debate: list) -> dict:
        debate_text = "\n\n".join([f"**{h['role']}**: {h['content']}" for h in full_debate])
        system = """You are an impartial debate judge. Evaluate the debate and return JSON:
{"winner": "agent_name", "reasoning": "why they won", "scores": {"agent1": 0-10, "agent2": 0-10, "agent3": 0-10}, "key_arguments": ["best argument 1", "best argument 2"], "weaknesses": ["weakness 1"]}"""
        messages = [{"role": "system", "content": system}, {"role": "user", "content": f"TOPIC: {topic}\n\nDEBATE:\n{debate_text}"}]
        result = await self.chat(messages, temperature=0.3)
        try:
            return json.loads(result.strip().strip("```json").strip("```"))
        except:
            return {"winner": "undetermined", "reasoning": result[:200], "scores": {}, "key_arguments": [], "weaknesses": []}
