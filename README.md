# ecomb

```bash
# build
docker build -t <name> .

# run
docker run --env driver_path="/usr/local/bin/chromedriver" --shm-size="2g" <name>:latest
```