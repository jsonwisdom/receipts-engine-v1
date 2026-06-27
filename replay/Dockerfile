FROM python:3.12.4-slim@sha256:3072fc8ecbfb662b3510c19d17b00c737128de7c4f60147ffaf349cb38ca9c7aa

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

WORKDIR /repo

COPY replay/verify_replay.py /repo/replay/verify_replay.py
COPY replay/replay_manifest.json /repo/replay/replay_manifest.json
COPY anchors /repo/anchors
COPY checkpoint /repo/checkpoint

CMD ["python", "replay/verify_replay.py", "--manifest", "replay/replay_manifest.json"]
