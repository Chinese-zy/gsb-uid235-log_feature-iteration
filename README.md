按行收日志，一行就当成一条。多行的记录和堆栈会散开。

记号是井号、序号、空格、正文长度，然后是那么多个字节。容器用下面这条拉起，收取口不要换。

```
docker compose up --build -d
```

宿主机页在 http://127.0.0.1:8765/ ，收取是 POST /ingest ，读出是 GET /records ，探活是 GET /health 。本机直接跑是 `python app.py`，听 8765。核对是 `python -m unittest`。失败点从 Splice 的 fail_at 注入，不要真去杀进程。
