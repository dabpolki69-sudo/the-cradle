from dataclasses import dataclass
from typing import Protocol, Optional

class Substrate(Protocol):
    name:str
    model_id:str
    def generate(self,prompt:str, *, system:Optional[str]=None)->str: ...

@dataclass
class ModelSpec:
    provider:str
    model_id:str
    role:str="general"
    language:bool=True

class SubstrateRegistry:
    """Provider-neutral registry. The Chorus chooses roles; substrates provide capability."""
    def __init__(self):
        self.models:dict[str,ModelSpec]={}

    def register(self,key:str,spec:ModelSpec):
        self.models[key]=spec

    def for_role(self,role:str):
        return [s for s in self.models.values() if s.role==role or s.role=="general"]

    def describe(self):
        return [{"provider":s.provider,"model_id":s.model_id,"role":s.role,"language":s.language}
                for s in self.models.values()]

# Hugging Face is intentionally an adapter, not a dependency of the architecture.
# HF Inference Providers can expose many open models behind a unified client.
# This class keeps credentials/configuration outside the cognitive core.
class HuggingFaceSubstrate:
    def __init__(self, client, model_id:str, role:str="general"):
        self.client=client
        self.model_id=model_id
        self.name=f"huggingface:{model_id}"
        self.role=role

    def generate(self,prompt:str, *, system=None)->str:
        messages=[]
        if system: messages.append({"role":"system","content":system})
        messages.append({"role":"user","content":prompt})
        result=self.client.chat.completions.create(model=self.model_id,messages=messages)
        return result.choices[0].message.content or ""
