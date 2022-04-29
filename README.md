# ecomb

```bash
# build
docker build -t <name> .

# run
docker run -e dotenv_path=/app/data/.env -v </absolute/path/to>/resources/env-volume:/app/data --shm-size="2g" <name>:latest
```