# Type stubs for together AI library
from typing import Any, Dict, List, Optional, Union

class Together:
    def __init__(self, api_key: Optional[str] = None) -> None: ...

    def chat_completion(self,
                       messages: List[Dict[str, Any]],
                       model: str,
                       max_tokens: Optional[int] = None,
                       temperature: Optional[float] = None,
                       top_p: Optional[float] = None,
                       **kwargs: Any) -> Dict[str, Any]: ...

    def models_list(self) -> Dict[str, List[Dict[str, Any]]]: ...

class AsyncTogether:
    def __init__(self, api_key: Optional[str] = None) -> None: ...

    async def chat_completion(self,
                             messages: List[Dict[str, Any]],
                             model: str,
                             max_tokens: Optional[int] = None,
                             temperature: Optional[float] = None,
                             top_p: Optional[float] = None,
                             **kwargs: Any) -> Dict[str, Any]: ...

    async def models_list(self) -> Dict[str, List[Dict[str, Any]]]: ...