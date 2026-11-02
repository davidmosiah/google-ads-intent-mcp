"""Real SDK contract, using an injected local classifier only."""
import asyncio
import pytest

pytest.importorskip('mcp')
from google_ads_intent_mcp import intent, mcp_server


def test_real_sdk_preserves_llm_optout_and_nullable_schema(monkeypatch):
    monkeypatch.setenv('GOOGLE_ADS_INTENT_LLM', 'true')
    calls = []
    monkeypatch.setattr(intent, '_default_llm_classifier', lambda: lambda term: calls.append(term) or 'competitor')

    async def check():
        mcp = mcp_server.create_mcp()
        tools = await mcp.list_tools()
        names = {'google_ads_classify_search_term', 'google_ads_analyze_search_terms', 'google_ads_build_negative_plan'}
        assert names <= {tool.name for tool in tools}
        for tool in tools:
            if tool.name in names:
                schema = tool.inputSchema['properties']['llm']
                assert schema['default'] is None
                assert {'type': 'boolean'} in schema['anyOf']
                assert {'type': 'null'} in schema['anyOf']
        for name, args in [
            ('google_ads_classify_search_term', {'term': 'synthetic'}),
            ('google_ads_analyze_search_terms', {'rows': [{'search_term': 'synthetic'}]}),
            ('google_ads_build_negative_plan', {'rows': [{'search_term': 'synthetic'}]}),
        ]:
            before = len(calls)
            await mcp.call_tool(name, {**args, 'llm': False})
            assert len(calls) == before
            await mcp.call_tool(name, {**args, 'llm': True})
            await mcp.call_tool(name, {**args, 'llm': None})
            await mcp.call_tool(name, args)
            assert len(calls) == before + 3
    asyncio.run(check())
