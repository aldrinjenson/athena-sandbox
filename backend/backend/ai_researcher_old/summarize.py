"""
The summarize node is responsible for summarizing the information.
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from copilotkit.langchain import copilotkit_customize_config
from langchain_core.messages.ai import AIMessage
from .state import AgentState

async def summarize_node(state: AgentState, config: RunnableConfig):
    """
    The summarize node is responsible for summarizing the information.
    """

    # config = copilotkit_customize_config(
    #     config,
    #     emit_messages=True,
    #     # emit_state={
    #     #     "answer": {
    #     #         "tool": "summarize"
    #     #     },
    #     # }
    # )
    config = copilotkit_customize_config(config, emit_all=True)

    system_message = f"""
The system has performed a series of steps to answer the user's query.
These are all of the steps: {json.dumps(state["steps"])}

Please summarize the final result and include all relevant information and reference links.
"""

    summarize_tool = {
        'name': 'summarize',
        'description': """
Summarize the final result. Make sure that the summary is complete and includes all relevant information and reference links.
""",
        'parameters': {
            'type': 'object',
            'properties': {
                'markdown': {
                    'description': 'The markdown formatted summary of the final result. If you add any headings, make sure to start at the top level (#)',
                    'type': 'string'
                },
                'references': {
                    'description': """A list of references.""",
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            
                            'title': {
                                'description': 'The title of the reference.',
                                'type': 'string'
                            },
                            'url': {
                                'description': 'The url of the reference.',
                                'type': 'string'
                            },
                        },
                        'required': ['title', 'url']
                    }
                }
            },
            'required': ['markdown', 'references']
        }
    }

    response = await ChatOpenAI(model="gpt-4o").bind_tools([summarize_tool], tool_choice="summarize").ainvoke([
        *state["messages"],
        SystemMessage(
            content=system_message
        )
    ], config)

    return {
        "messages": [           
            response,
            ToolMessage(
                name=response.tool_calls[0]["name"],
                content=response.tool_calls[0]["args"]["markdown"],
                tool_call_id=response.tool_calls[0]["id"]
            )
        ],
        "answer": response.tool_calls[0]["args"],
    }
