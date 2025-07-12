from langchain.llms.base import LLM
from typing import Optional, List, Any
from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM
from langchain_core.callbacks.base import Callbacks
from pydantic import Field
import os


class OpenVinoLangChainLLM(LLM):
    # Required LangChain fields
    callbacks: Optional[Callbacks] = Field(default=None, exclude=True)
    verbose: Optional[bool] = Field(default=False, exclude=True)

    # Internal model and tokenizer
    tokenizer: Any = Field(default=None, exclude=True)
    model: Any = Field(default=None, exclude=True)

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

        os.environ["OMP_NUM_THREADS"] = "4"
        os.environ["OPENVINO_NUM_STREAMS"] = "1"

        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_id, trust_remote_code=True)
        self.model = OVModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)
        self.model.compile()

    @property
    def _llm_type(self) -> str:
        return "openvino-phi3-128k"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)

        
        max_new_tokens = min(1024, 128000 - len(inputs["input_ids"][0]))

        # Generate output
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            return_dict_in_generate=False,
            eos_token_id=self.tokenizer.eos_token_id,
        )

       
        full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

     
        index = full_text.rfind(prompt)
        if index != -1:
            return full_text[index + len(prompt):].strip()
        else:
            return full_text.strip()

    @property
    def _identifying_params(self) -> dict:
        return {
            "model_id": "OpenVINO/Phi-3-mini-128k-instruct-int8-ov",
            "tokenizer_id": "microsoft/Phi-3-mini-128k-instruct"
        }
