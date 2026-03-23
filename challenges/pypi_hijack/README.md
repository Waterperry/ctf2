This challenge involves uploading a malicious Python package to a package repository that exploits
the vulnerability used in the recent LiteLLM supply chain compromise. A second system will repeatedly
set up a new `uv` / `python` project and install `numpy`, then run a Python program (that does NOT import numpy),
so to compromise this machine the attacker has to submit a package with malicious code embedded in a PTH file within
the Python wheel.
