# Fetch Rewards Receipt Processor Challenge
A solution for the Fetch Rewards backend test. Dockerized and exposed on port 8000.

## Build

```bash
docker build -f Dockerfile . -t sam-huffman-receipt-processor:1
```

## Run

```bash
docker run -it -p 8000:8000 sam-huffman-receipt-processor:1
```
