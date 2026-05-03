import time
from collections.abc import Iterator

import httpx

from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


class HevyClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._http = httpx.Client(
            base_url=config.base_url,
            headers={"api-key": config.api_key},
            timeout=30.0,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "HevyClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get(self, path: str, params: dict | None = None, retries: int = 3) -> dict:
        for attempt in range(retries):
            try:
                resp = self._http.get(path, params=params)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    wait = 2**attempt
                    logger.warning(f"Rate limited – waiting {wait}s (attempt {attempt + 1})")
                    time.sleep(wait)
                    continue
                raise
            except httpx.TransportError:
                if attempt == retries - 1:
                    raise
                time.sleep(1)
        raise RuntimeError(f"GET {path} failed after {retries} attempts")  # unreachable

    def _put(self, path: str, body: dict, retries: int = 3) -> dict:
        for attempt in range(retries):
            try:
                resp = self._http.put(path, json=body)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 400:
                    logger.error(
                        f"PUT {path} → 400 Bad Request | "
                        f"response: {exc.response.json()} | "
                        f"body: {body}"
                    )
                    raise
                if status == 429:
                    wait = 2**attempt
                    logger.warning(f"Rate limited – waiting {wait}s (attempt {attempt + 1})")
                    time.sleep(wait)
                    continue
                logger.error(f"PUT {path} → {status} | response: {exc.response.text}")
                raise
            except httpx.TransportError as exc:
                logger.warning(f"PUT {path} transport error (attempt {attempt + 1}/{retries}): {exc}")
                if attempt == retries - 1:
                    raise
                time.sleep(1)
        raise RuntimeError(f"PUT {path} failed after {retries} attempts")

    def iter_workouts(self) -> Iterator[dict]:
        page = 1
        while True:
            data = self._get("/v1/workouts", params={"page": page, "pageSize": self._config.page_size})
            workouts = data.get("workouts", [])
            yield from workouts
            if page >= data.get("page_count", 1):
                break
            page += 1
            logger.info(f"Fetched page {page - 1}/{data.get('page_count', 1)}")

    def update_workout(self, workout_id: str, workout: dict) -> dict:
        body = {
            "workout": {
                "title": workout.get("title", ""),
                #"description": workout.get("description"),
                "start_time": workout.get("start_time"),
                "end_time": workout.get("end_time"),
                "is_private": workout.get("is_private", False),
                "exercises": [
                    {
                        k: (
                            [
                                {sk: sv for sk, sv in s.items() if sk != "index"}
                                for s in v
                            ]
                            if k == "sets"
                            else ("dumbbell weight log rectified" if v == "" else v + " dumbbell weight log rectified")
                            if k == "notes"
                            else v
                        )
                        for k, v in ex.items()
                    }
                    for ex in workout.get("exercises", [])
                ],
            }
        }
        return self._put(f"/v1/workouts/{workout_id}", body)
