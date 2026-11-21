# Reproducible toolchain: the same versions the accuracy figures in
# docs/accuracy.md were measured with (clang/clang-tidy 19.1.7, cppcheck 2.17.1).
# Debian 13 (trixie) package versions are pinned; if the archive drops a pinned
# version, rebuild with the current one and re-run tools/eval_accuracy.py.
FROM debian:trixie-slim

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      git ca-certificates python3 python3-venv python3-pip \
      clang-19=1:19.1.7-3+b1 clang-tidy-19=1:19.1.7-3+b1 cppcheck=2.17.1-2 \
      libc6-dev libstdc++-14-dev libboost-dev libssl-dev \
 && ln -s /usr/bin/clang-19 /usr/local/bin/clang && ln -s /usr/bin/clang++-19 /usr/local/bin/clang++ \
 && ln -s /usr/bin/clang-tidy-19 /usr/local/bin/clang-tidy \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE NOTICE /opt/cert-review/
COPY src /opt/cert-review/src
COPY data /opt/cert-review/data
COPY profiles /opt/cert-review/profiles
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir /opt/cert-review

ENV CERT_REVIEW_HOME=/opt/cert-review PATH=/opt/venv/bin:$PATH
RUN clang-tidy --version | grep -q 'version 19.1.7' && cppcheck --version | grep -q '2.17.1'
ENTRYPOINT ["python3", "-m", "cert_review.action"]
