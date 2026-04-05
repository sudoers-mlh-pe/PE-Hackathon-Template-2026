to run the load test, follow these steps:

1. make sure your uv environment is synced
`uv sync`

2. Run the load test with the following command:

```bash
uv run locust --headless --users 50 --spawn-rate 10 --run-time 60s --host https://url-shortener.sabihinmolang.eu.org/ --csv=loadtest/results -f loadtest/test.py 
```