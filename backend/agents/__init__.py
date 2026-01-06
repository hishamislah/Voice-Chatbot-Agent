"""
Multi-agent system for chatbot with Personal Assistant, HR Agent, and IT Support Agent
"""

from .multi_agent_graph import (
    create_multi_agent_graph,
    MultiAgentState,
    route_from_hr_entry,
    route_from_hr_validation,
    route_from_it_entry,
    route_from_it_validation,
)
from .personal_assistant import personal_assistant_node, PersonalAssistantTools
from .specialist_agents import (
    hr_agent_entry_node,
    hr_clarification_node,
    hr_rag_retrieval_node,
    hr_answer_generation_node,
    hr_answer_generation_node_stream,
    hr_validation_node,
    hr_out_of_scope_node,
    it_agent_entry_node,
    it_clarification_node,
    it_rag_retrieval_node,
    it_answer_generation_node,
    it_answer_generation_node_stream,
    it_validation_node,
    it_out_of_scope_node,
)

__all__ = [
    "create_multi_agent_graph",
    "MultiAgentState",
    "route_from_hr_entry",
    "route_from_hr_validation",
    "route_from_it_entry",
    "route_from_it_validation",
    "personal_assistant_node",
    "PersonalAssistantTools",
    "hr_agent_entry_node",
    "hr_clarification_node",
    "hr_rag_retrieval_node",
    "hr_answer_generation_node",
    "hr_answer_generation_node_stream",
    "hr_validation_node",
    "hr_out_of_scope_node",
    "it_agent_entry_node",
    "it_clarification_node",
    "it_rag_retrieval_node",
    "it_answer_generation_node",
    "it_answer_generation_node_stream",
    "it_validation_node",
    "it_out_of_scope_node",
]
