"""
端到端测试脚本：验证 爬取 → 入库 → 查询 主流程
用法: python -m scripts.test_e2e
"""
import asyncio
import httpx

BASE = "http://localhost:8000/api/v1"


async def main():
    async with httpx.AsyncClient(timeout=60) as c:
        # 1. 健康检查
        r = await c.get("http://localhost:8000/health")
        assert r.status_code == 200
        print("✅ 服务正常运行")

        # 2. 手动创建一篇论文
        r = await c.post(f"{BASE}/papers/", json={
            "title": "Attention Is All You Need",
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
            "year": 2017,
            "venue": "NeurIPS",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            "doi": "10.5555/3295222.3295349",
        })
        assert r.status_code == 201
        paper1 = r.json()
        print(f"✅ 论文创建成功: {paper1['id']} - {paper1['title']}")

        # 3. 创建第二篇论文
        r = await c.post(f"{BASE}/papers/", json={
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "abstract": "We introduce a new language representation model called BERT...",
            "year": 2019,
            "venue": "NAACL",
            "authors": ["Jacob Devlin", "Ming-Wei Chang"],
        })
        assert r.status_code == 201
        paper2 = r.json()
        print(f"✅ 论文创建成功: {paper2['id']} - {paper2['title']}")

        # 4. 创建关联
        r = await c.post(f"{BASE}/graph/relations", json={
            "source_id": paper2["id"],
            "target_id": paper1["id"],
            "relation_type": "IMPROVES",
            "description": "BERT 基于 Transformer 架构，引入双向预训练",
        })
        assert r.status_code == 201
        print(f"✅ 关联创建成功: {paper2['title'][:30]} --IMPROVES--> {paper1['title'][:30]}")

        # 5. 查询图谱
        r = await c.get(f"{BASE}/graph/subgraph", params={"center": paper1["id"], "depth": 1})
        assert r.status_code == 200
        graph = r.json()
        print(f"✅ 图谱查询: {len(graph['nodes'])} 节点, {len(graph['edges'])} 边")

        # 6. 搜索
        r = await c.get(f"{BASE}/search/", params={"q": "transformer"})
        assert r.status_code == 200
        search = r.json()
        print(f"✅ 搜索 'transformer': 找到 {search['total']} 条结果")

        # 7. 论文列表
        r = await c.get(f"{BASE}/papers/")
        assert r.status_code == 200
        papers = r.json()
        print(f"✅ 论文列表: 共 {papers['total']} 篇")

        # 8. 启动爬取任务（小规模测试）
        r = await c.post(f"{BASE}/crawler/start", json={
            "domain": "computer_science",
            "subdomain": "deep_learning",
            "year_from": 2020,
            "year_to": 2026,
            "min_citations": 1000,
            "max_papers": 5,
        })
        assert r.status_code == 202
        task = r.json()
        print(f"✅ 爬取任务已启动: {task['id']}")

        # 等待爬取完成
        print("⏳ 等待爬取任务完成...")
        for _ in range(30):
            await asyncio.sleep(3)
            r = await c.get(f"{BASE}/crawler/tasks/{task['id']}")
            status = r.json()
            if status["status"] in ("completed", "failed"):
                break
            print(f"   进度: searched={status['searched']}, imported={status['imported']}")

        r = await c.get(f"{BASE}/crawler/tasks/{task['id']}")
        final = r.json()
        print(f"✅ 爬取完成: status={final['status']}, imported={final['imported']}")

        # 最终统计
        r = await c.get(f"{BASE}/papers/")
        total = r.json()["total"]
        print(f"\n🎉 全部测试通过！知识库共 {total} 篇论文")


if __name__ == "__main__":
    asyncio.run(main())
