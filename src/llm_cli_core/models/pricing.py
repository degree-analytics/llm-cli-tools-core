"""Model pricing cache and estimation utilities."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

import httpx

from llm_cli_core.config import Config, get_config

logger = logging.getLogger(__name__)

LITELLM_PRICING_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
)
OPENROUTER_PRICING_URL = "https://openrouter.ai/api/v1/models"
CACHE_FILENAME = "pricing.json"
REFRESH_INTERVAL = timedelta(days=7)


@dataclass
class ModelPricing:
    prompt: Optional[float]
    completion: Optional[float]
    request: Optional[float] = None
    source: str = "litellm"

    def estimate(self, *, input_tokens: int, output_tokens: int) -> Optional[float]:
        total = 0.0
        have_cost = False
        if self.prompt is not None:
            total += self.prompt * input_tokens
            have_cost = True
        if self.completion is not None:
            total += self.completion * output_tokens
            have_cost = True
        if self.request is not None:
            total += self.request
            have_cost = True
        return total if have_cost else None


class PricingCache:
    """Maintains locally cached pricing metadata."""

    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or get_config()
        self.cache_path = self.config.resolve_cache_dir() / CACHE_FILENAME
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._models: Dict[str, ModelPricing] = {}
        self._fetched_at: Optional[datetime] = None

    def load(self, force: bool = False) -> Dict[str, ModelPricing]:
        if not force and self._models and not self._is_stale(self._fetched_at):
            return self._models

        if not force and self.cache_path.exists():
            try:
                cached = json.loads(self.cache_path.read_text(encoding="utf-8"))
                fetched_at = _parse_dt(cached.get("fetched_at"))
                if not self._is_stale(fetched_at):
                    models = {
                        key: ModelPricing(**value)
                        for key, value in cached.get("models", {}).items()
                    }
                    self._models = models
                    self._fetched_at = fetched_at
                    return self._models
            except Exception as exc:
                logger.debug(f"Failed to load pricing cache: {exc}")

        models, fetched_at = self._fetch_remote()
        self._models = models
        self._fetched_at = fetched_at
        self._persist_cache()
        return self._models

    def estimate_cost(
        self, model: str, *, input_tokens: int, output_tokens: int
    ) -> Optional[float]:
        if not model:
            return None
        model = model.strip()
        if not model:
            return None

        models = self.load()
        lookup = self._lookup_model(models, model)
        if not lookup:
            return None
        return lookup.estimate(input_tokens=input_tokens, output_tokens=output_tokens)

    def _lookup_model(
        self, models: Dict[str, ModelPricing], model: str
    ) -> Optional[ModelPricing]:
        key = model.lower()
        query_tokens = _normalise_key(key)

        for token in query_tokens:
            if token in models:
                return models[token]

        for candidate_key, pricing in models.items():
            candidate_tokens = _normalise_key(candidate_key)
            if query_tokens & candidate_tokens:
                return pricing
        return None

    def _persist_cache(self) -> None:
        if not self._models or not self._fetched_at:
            return
        payload = {
            "fetched_at": self._fetched_at.isoformat(),
            "models": {key: asdict(value) for key, value in self._models.items()},
        }
        self.cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _is_stale(self, fetched_at: Optional[datetime]) -> bool:
        if fetched_at is None:
            return True
        return datetime.now(timezone.utc) - fetched_at > REFRESH_INTERVAL

    def _fetch_remote(self) -> Tuple[Dict[str, ModelPricing], datetime]:
        models: Dict[str, ModelPricing] = {}
        fetched_at = datetime.now(timezone.utc)

        with httpx.Client(timeout=10.0) as client:
            try:
                response = client.get(LITELLM_PRICING_URL)
                response.raise_for_status()
                data = response.json()
                for key, info in data.items():
                    prompt = info.get("input_cost_per_token")
                    completion = info.get("output_cost_per_token")
                    request_cost = info.get("request_cost")
                    if prompt is None and completion is None and request_cost is None:
                        continue
                    models[key.lower()] = ModelPricing(
                        prompt=float(prompt) if prompt is not None else None,
                        completion=float(completion) if completion is not None else None,
                        request=float(request_cost) if request_cost is not None else None,
                        source="litellm",
                    )
            except Exception as exc:
                logger.warning(f"Failed to refresh litellm pricing map: {exc}")

            try:
                response = client.get(OPENROUTER_PRICING_URL)
                response.raise_for_status()
                data = response.json().get("data", [])
                for item in data:
                    pricing = item.get("pricing") or {}
                    prompt = pricing.get("prompt")
                    completion = pricing.get("completion")
                    request_cost = pricing.get("request")

                    def _to_float(value: Optional[str]) -> Optional[float]:
                        if value in (None, "", "0"):
                            return None
                        try:
                            return float(value)
                        except ValueError:
                            return None

                    prompt_cost = _to_float(prompt)
                    completion_cost = _to_float(completion)
                    request_float = _to_float(request_cost)

                    if prompt_cost is None and completion_cost is None and request_float is None:
                        continue

                    models[item["id"].lower()] = ModelPricing(
                        prompt=prompt_cost,
                        completion=completion_cost,
                        request=request_float,
                        source="openrouter",
                    )
            except Exception as exc:
                logger.warning(f"Failed to refresh OpenRouter pricing data: {exc}")

        return models, fetched_at


_pricing_cache: Optional[PricingCache] = None


def get_pricing_cache() -> PricingCache:
    global _pricing_cache
    if _pricing_cache is None:
        _pricing_cache = PricingCache()
    return _pricing_cache


def _normalise_key(value: str) -> set[str]:
    value = value.lower().strip()
    if not value:
        return set()

    tokens = {value}
    for sep in (":", "/", "."):
        if sep in value:
            parts = value.split(sep)
            if parts and parts[-1]:
                tokens.add(parts[-1])
            tokens.add(".".join(parts))

    tokens.add(value.replace(":", "."))
    tokens.add(value.replace("/", "."))
    tokens.add(value.replace(":", "/"))

    if "-" in value:
        segments = value.split("-")
        for i in range(len(segments), 0, -1):
            candidate = "-".join(segments[:i])
            if candidate:
                tokens.add(candidate)

    return {token for token in tokens if token}


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


__all__ = [
    "ModelPricing",
    "PricingCache",
    "get_pricing_cache",
]
