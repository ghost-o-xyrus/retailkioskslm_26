"""Model registry. Adapters import their framework lazily inside load()."""
from .base import ModelAdapter
from .template_baseline import TemplateBaseline


def build(name: str, **kw) -> ModelAdapter:
    if name == "template_baseline":
        return TemplateBaseline(**kw)
    if name == "cardiogan":
        from .cardiogan import CardioGAN
        return CardioGAN(**kw)
    if name == "ppgflowecg":
        from .ppgflowecg import PPGFlowECG
        return PPGFlowECG(**kw)
    if name in ("chiu2020", "clep_gan", "p2e_wgan", "yalcin2026"):
        from .trained import TRAINED
        return TRAINED[name](**kw)
    if name == "zhu_dct":
        from .zhu_dct import ZhuDCT
        return ZhuDCT(**kw)
    if name == "rddm":
        from .rddm import RDDM
        return RDDM(**kw)
    if name == "onnx":
        from .onnx_generic import OnnxModel
        return OnnxModel(**kw)
    raise KeyError(f"unknown model '{name}'")
