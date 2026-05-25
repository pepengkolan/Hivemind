'''Debate history storage — SQLite for persistence.'''

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "debates.db"


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS debates (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        rounds INTEGER DEFAULT 3,
        status TEXT DEFAULT 'running',
        history TEXT DEFAULT '[]',
        judgment TEXT DEFAULT '{}',
        agents TEXT DEFAULT '[]',
        tokens_used INTEGER DEFAULT 0,
        created_at TEXT,
        completed_at TEXT
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        debate_id TEXT,
        agent_name TEXT,
        voter_ip TEXT,
        created_at TEXT,
        FOREIGN KEY (debate_id) REFERENCES debates(id)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS leaderboard (
        agent_name TEXT PRIMARY KEY,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        draws INTEGER DEFAULT 0,
        total_debates INTEGER DEFAULT 0,
        avg_score REAL DEFAULT 0
    )''')
    conn.commit()
    conn.close()


def save_debate(debate: dict):
    conn = get_db()
    conn.execute('''INSERT OR REPLACE INTO debates (id, topic, rounds, status, history, judgment, agents, tokens_used, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        debate['id'], debate['topic'], debate['rounds'], debate['status'],
        json.dumps(debate['history']), json.dumps(debate.get('judgment', {})),
        json.dumps(debate['agents']), int(debate.get('total_tokens_estimated', 0)),
        debate.get('started_at', ''), debate.get('completed_at', '')
    ))
    conn.commit()
    conn.close()


def get_debate(debate_id: str) -> dict:
    conn = get_db()
    row = conn.execute('SELECT * FROM debates WHERE id = ?', (debate_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['history'] = json.loads(d['history'])
        d['judgment'] = json.loads(d['judgment'])
        d['agents'] = json.loads(d['agents'])
        return d
    return None


def list_debates(limit: int = 20) -> list:
    conn = get_db()
    rows = conn.execute('SELECT id, topic, status, judgment, created_at FROM debates ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d['judgment'] = json.loads(d['judgment'])
        results.append(d)
    return results


def vote(debate_id: str, agent_name: str, voter_ip: str):
    conn = get_db()
    conn.execute('INSERT INTO votes (debate_id, agent_name, voter_ip, created_at) VALUES (?, ?, ?, ?)',
                 (debate_id, agent_name, voter_ip, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_votes(debate_id: str) -> dict:
    conn = get_db()
    rows = conn.execute('SELECT agent_name, COUNT(*) as count FROM votes WHERE debate_id = ? GROUP BY agent_name', (debate_id,)).fetchall()
    conn.close()
    return {row['agent_name']: row['count'] for row in rows}


def update_leaderboard(winner: str, scores: dict):
    conn = get_db()
    for agent, score in scores.items():
        conn.execute('''INSERT INTO leaderboard (agent_name, wins, losses, draws, total_debates, avg_score)
            VALUES (?, ?, ?, ?, 1, ?)
            ON CONFLICT(agent_name) DO UPDATE SET
            wins = wins + ?, losses = losses + ?, draws = draws + ?,
            total_debates = total_debates + 1,
            avg_score = (avg_score * (total_debates - 1) + ?) / total_debates''', (
            agent, 1 if agent == winner else 0, 0 if agent == winner else 1, 0,
            score, 1 if agent == winner else 0, 0 if agent == winner else 1, 0, score
        ))
    conn.commit()
    conn.close()


def get_leaderboard() -> list:
    conn = get_db()
    rows = conn.execute('SELECT * FROM leaderboard ORDER BY wins DESC, avg_score DESC').fetchall()
    conn.close()
    return [dict(row) for row in rows]
