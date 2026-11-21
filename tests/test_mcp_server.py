"""MCP server: in-process calls plus a real stdio round trip."""
import asyncio
import json
import sys

import pytest

from cert_review.mcp_server import build_server

EXPECTED_TOOLS = {"list_rules", "explain_rule", "search_rules", "check_file", "check_diff",
                  "review_packet", "validate_findings", "rule_coverage", "format_review"}


def _text(result):
    return result.content[0].text


def test_tools_resources_prompts_registered():
    s = build_server()

    async def go():
        tools = {t.name for t in await s.list_tools()}
        templates = {t.uri_template for t in await s.list_resource_templates()}
        prompts = {p.name for p in await s.list_prompts()}
        return tools, templates, prompts
    tools, templates, prompts = asyncio.run(go())
    assert tools == EXPECTED_TOOLS
    assert {"rule://{rule_id}", "profile://{name}"} <= templates
    assert {"cert_review", "ceph_review"} <= prompts


def test_explain_and_list_in_process():
    s = build_server()

    async def go():
        a = json.loads(_text(await s.call_tool("explain_rule", {"id": "EXP34-C"})))
        b = json.loads(_text(await s.call_tool(
            "list_rules", {"lang": "cpp", "coverage": "deterministic", "limit": 100})))
        c = json.loads(_text(await s.call_tool("rule_coverage", {"lang": "cpp"})))
        return a, b, c
    a, b, c = asyncio.run(go())
    assert a["risk"]["priority"] == "P18" and a["coverage"]["checkers"]
    assert b["count"] == 18 and all(r["lang"] == "cpp" for r in b["rules"])
    assert c["total"] == 83


def test_prompts_forbid_posting():
    s = build_server()

    async def go():
        return await s.get_prompt("ceph_review", {"target": "my PR"})
    p = asyncio.run(go())
    text = json.dumps(p, default=str)
    assert "never post" in text.lower() and "ceph_assert" in text


def test_stdio_round_trip():
    from mcp import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    async def go():
        params = StdioServerParameters(command=sys.executable, args=["-m", "cert_review.mcp_server"])
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                tools = {t.name for t in (await session.list_tools()).tools}
                res = await session.call_tool("search_rules", {"query": "null pointer dereference", "limit": 3})
                rr = await session.read_resource("rule://EXP34-C")
                return tools, json.loads(res.content[0].text), rr
    try:
        tools, search, rr = asyncio.run(asyncio.wait_for(go(), 60))
    except Exception as e:     # SDK client API differs between releases; do not hide real failures
        pytest.skip(f"mcp client API unavailable: {type(e).__name__}: {e}") if "attribute" in str(e) else None
        raise
    assert tools == EXPECTED_TOOLS
    assert any(x["id"] == "EXP34-C" for x in search["results"])
    assert "EXP34-C" in str(rr)
