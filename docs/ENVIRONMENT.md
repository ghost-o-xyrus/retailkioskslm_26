# Environment the results were measured in

Written by `publish/prepare_repo.py` on the test laptop. Both tiers were measured on this one machine.

| | |
|---|---|
| Processor | 12th Gen Intel(R) Core(TM) i5-1240P |
| Memory | 16 GB |
| Graphics | Parsec Virtual Display Adapter / Intel(R) Iris(R) Xe Graphics |
| Operating system | Windows 11 (10.0.26300) |
| Python | 3.13.1 |
| llama.cpp | b11696 |

## Packages the kiosk uses at run time

```
numpy==2.4.6
openvino==2026.4.1
tokenizers==0.22.2
psutil==7.2.2
```

## Every package in the project's environment (`pip freeze`)

The evaluation, retrieval-building and write-up tools need more than the kiosk does.

```
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
axe-playwright-python==0.1.8
certifi==2026.10.18
charset-normalizer==3.5.2
click==8.5.0
cloudpickle==3.1.2
colorama==0.4.6
contourpy==1.4.0
cycler==0.12.1
et_xmlfile==2.0.0
filelock==4.2.0
flatbuffers==25.12.19
fonttools==4.67.0
fsspec==2026.9.0
greenlet==3.5.6
h11==0.16.0
hf-xet==1.7.0
httpcore==1.0.9
httpcore2==2.13.1
httpx==0.28.1
httpx2==2.13.1
huggingface_hub==0.36.2
idna==3.20
Jinja2==3.1.6
jiter==0.17.0
joblib==1.6.0
kiwisolver==1.5.1
markdown-it-py==4.2.0
MarkupSafe==3.0.4
matplotlib==3.11.2
mdurl==0.1.2
ml_dtypes==0.6.0
mpmath==1.3.0
narwhals==2.27.1
networkx==3.6.1
ninja==1.13.2
nncf==3.4.0
numpy==2.4.6
onnx==1.23.2
onnxruntime==1.31.0
openai==3.33.0
openpyxl==3.1.5
openvino==2026.4.1
openvino-telemetry==2025.2.0
openvino-tokenizers==2026.4.1.0
optimum==2.3.0
optimum-intel==2.2.0
optimum-onnx==0.1.0
packaging==26.3
pandas==3.0.6
pillow==13.0.0
playwright==1.64.1
protobuf==7.36.2
psutil==7.2.2
pydantic==2.14.1
pydantic_core==2.50.1
pydot==4.0.1
pyee==14.0.0
Pygments==2.21.0
pyparsing==3.3.3
python-dateutil==2.9.0.post0
PyYAML==6.0.3
regex==2026.9.29
requests==2.34.2
rich==15.0.0
safetensors==0.8.0
scikit-learn==1.9.1
scipy==1.18.1
sentence-transformers==5.7.0
setuptools==84.0.0
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
sympy==1.14.0
tabulate==0.10.0
threadpoolctl==3.7.0
tokenizers==0.22.2
torch==2.14.1
torchvision==0.29.1
tqdm==4.70.1
transformers==4.57.6
truststore==0.10.5
typer==0.27.3
typing-inspection==0.4.4
typing_extensions==4.16.0
tzdata==2026.5
urllib3==2.8.0
```

