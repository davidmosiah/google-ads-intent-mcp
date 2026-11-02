"""No provider calls: fake MCP registration and classifier capture only."""
import sys
import types

from google_ads_intent_mcp import mcp_server


def test_mcp_preserves_explicit_llm_optout(monkeypatch):
    registered = {}

    class FakeMCP:
        def __init__(self, name):
            self.name = name

        def tool(self):
            def register(fn):
                registered[fn.__name__] = fn
                return fn
            return register

    module = types.ModuleType('mcp.server.fastmcp')
    module.FastMCP = FakeMCP
    monkeypatch.setitem(sys.modules, 'mcp.server.fastmcp', module)
    monkeypatch.setenv('GOOGLE_ADS_INTENT_LLM', 'true')
    seen = []

    def capture(value, *, llm):
        seen.append(llm)
        return {}

    monkeypatch.setattr(mcp_server, 'classify_search_term', capture)
    monkeypatch.setattr(mcp_server, 'analyze_search_terms', capture)
    monkeypatch.setattr(mcp_server, 'build_negative_plan', lambda value, **kwargs: value)
    mcp_server.create_mcp()
    calls = [
        ('google_ads_classify_search_term', 'synthetic'),
        ('google_ads_analyze_search_terms', []),
        ('google_ads_build_negative_plan', []),
    ]
    for name, value in calls:
        registered[name](value, llm=False)
        registered[name](value, llm=True)
        registered[name](value)
    assert seen == [False, True, None] * 3
