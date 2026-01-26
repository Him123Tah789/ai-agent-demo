# Simple in-memory store (server-side)
agent_memory = []

def add_to_memory(agent_type, message):
    agent_memory.append({
        "agent_type": agent_type,
        "message": message
    })

def get_recent_memory(limit=3):
    return agent_memory[-limit:]
