import logging
from typing import Optional, Dict, Any
from backend.app.config import settings

logger = logging.getLogger("observability.langfuse")

try:
    from langfuse import Langfuse
except ImportError:
    Langfuse = None


class LangfuseTracer:
    _client = None
    _traces: Dict[str, Any] = {}

    @classmethod
    def get_client(cls):
        if not settings.langfuse_enabled:
            return None
        if not settings.langfuse_public_key or not settings.langfuse_secret_key:
            return None
        if cls._client is None and Langfuse:
            try:
                cls._client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host,
                )
                logger.info("Langfuse tracer initialized successfully with project credentials")
            except Exception as e:
                logger.warning(f"Failed to initialize Langfuse client: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def create_trace(cls, repair_id: str, metadata: Dict[str, Any] = None):
        client = cls.get_client()
        if not client:
            return None
        try:
            # Langfuse v4 observation API
            if hasattr(client, "start_observation"):
                obs = client.start_observation(
                    name=f"repair_{repair_id}",
                    as_type="span",
                    input={"repair_id": repair_id, **(metadata or {})},
                    metadata=metadata or {},
                )
                cls._traces[repair_id] = obs
                return obs
            # Legacy v2/v3 API fallback
            elif hasattr(client, "trace"):
                trace = client.trace(
                    name=f"repair_{repair_id}",
                    id=repair_id,
                    metadata=metadata or {},
                )
                cls._traces[repair_id] = trace
                return trace
            return None
        except Exception as e:
            logger.warning(f"Error creating Langfuse trace: {e}")
            return None

    @classmethod
    def log_span(cls, trace, name: str, input_data: Any = None, output_data: Any = None, metadata: Dict[str, Any] = None):
        if not trace:
            return None
        try:
            if hasattr(trace, "start_observation"):
                span = trace.start_observation(
                    name=name,
                    as_type="span",
                    input=input_data,
                    metadata=metadata or {},
                )
                if output_data is not None:
                    span.update(output=output_data)
                span.end()
                return span
            elif hasattr(trace, "span"):
                span = trace.span(name=name, input=input_data, output=output_data, metadata=metadata or {})
                span.end()
                return span
            return None
        except Exception as e:
            logger.warning(f"Error logging Langfuse span {name}: {e}")
            return None

    @classmethod
    def log_generation(
        cls,
        trace,
        name: str,
        model: str,
        input_data: Any,
        output_data: Any,
        usage: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        if not trace:
            return None
        try:
            if hasattr(trace, "start_observation"):
                gen = trace.start_observation(
                    name=name,
                    as_type="generation",
                    model=model,
                    input=input_data,
                    metadata=metadata or {},
                )
                update_kwargs = {}
                if output_data is not None:
                    update_kwargs["output"] = output_data
                if usage:
                    update_kwargs["usage"] = usage
                if update_kwargs:
                    gen.update(**update_kwargs)
                gen.end()
                return gen
            elif hasattr(trace, "generation"):
                gen = trace.generation(
                    name=name,
                    model=model,
                    input=input_data,
                    output=output_data,
                    usage=usage,
                    metadata=metadata or {},
                )
                gen.end()
                return gen
            return None
        except Exception as e:
            logger.warning(f"Error logging Langfuse generation {name}: {e}")
            return None

    @classmethod
    def flush(cls):
        client = cls.get_client()
        if client and hasattr(client, "flush"):
            try:
                client.flush()
            except Exception as e:
                logger.warning(f"Error flushing Langfuse client: {e}")

    @classmethod
    def get_trace_url(cls, trace_id: str) -> Optional[str]:
        client = cls.get_client()
        if not client:
            return None
        try:
            if hasattr(client, "get_trace_url"):
                return client.get_trace_url(trace_id=trace_id)
        except Exception:
            pass

        base = settings.langfuse_host.rstrip("/")
        return f"{base}/project/traces/{trace_id}"
