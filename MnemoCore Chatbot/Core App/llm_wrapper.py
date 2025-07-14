from langchain.llms.base import LLM
from typing import Optional, List, Any, ClassVar
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM
from langchain_core.callbacks.base import Callbacks
from pydantic import Field
import os
import threading


class OpenVinoLangChainLLM(LLM):
   
    callbacks: Optional[Callbacks] = Field(default=None, exclude=True)
    verbose: Optional[bool] = Field(default=False, exclude=True)

    
    tokenizer: Any = Field(default=None, exclude=True)
    model: Any = Field(default=None, exclude=True)

    
    model_lock: ClassVar[threading.Lock] = threading.Lock()

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    def __init__(
        self,
        model_id: str = "OpenVINO/Phi-3-mini-128k-instruct-int8-ov",
        tokenizer_id: str = "microsoft/Phi-3-mini-128k-instruct",
        callbacks: Optional[Callbacks] = None,
        verbose: Optional[bool] = False,
    ):
        super().__init__(callbacks=callbacks, verbose=verbose)

        #Optimising the code for low-end CPU
        os.environ["OMP_NUM_THREADS"] = "4"
        os.environ["OPENVINO_NUM_STREAMS"] = "1"

        
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_id, trust_remote_code=True)
        self.model = OVModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        self.model.compile()

    @property
    def _llm_type(self) -> str:
        return "openvino-phi3-128k"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        #Tokenising the prompt
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        max_new_tokens = min(1024, 128000 - len(inputs["input_ids"][0]))

        
        with self.model_lock:
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                return_dict_in_generate=False,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode and return generated text
        text = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return text[len(prompt):].strip() if text.startswith(prompt) else text.strip()

    @property
    def _identifying_params(self) -> dict:
        return {
            "model_id": "OpenVINO/Phi-3-mini-128k-instruct-int8-ov",
            "tokenizer_id": "microsoft/Phi-3-mini-128k-instruct"
        }
