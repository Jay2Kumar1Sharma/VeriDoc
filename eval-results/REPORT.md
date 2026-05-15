# VeriDoc Eval Report

Generated: 2026-05-16T00:00:00+00:00

This report file is committed so reviewers can see the expected output shape from `backend/scripts/eval.py`. It should be regenerated after copying `backend/.env.example` to `backend/.env`, adding an LLM API key, ingesting the corpus, and running:

```bash
cd backend
.venv\Scripts\python.exe scripts\eval.py
```

| Metric | Score |
| --- | ---: |
| Retrieval recall@5 | pending |
| Grounding rate | pending |
| Judge correctness | pending |

| Question | Expected chunk | Retrieved | Grounded | Correct |
| --- | --- | --- | --- | --- |
| How do I declare a FastAPI path parameter? | fastapi-tiangolo-com-tutorial-path-params_0000 | pending | pending | pending |
| What is a request body in FastAPI? | fastapi-tiangolo-com-tutorial-body_0000 | pending | pending | pending |
