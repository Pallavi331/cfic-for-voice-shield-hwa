# Contribution workflow
Each member works on a dedicated branch and opens a PR into `main`.

- `contrib/project-lead-cfic`: CFIC API, auth/rate limiting, orchestration, hosted LLM, TCED and end-to-end tests.
- `contrib/varun-pellav2-quantization`: exact PellaV2 artifact, quantization, comparison report and artifact manifest.
- `contrib/varshu-pellav2-docker`: detector Docker service, health/inference endpoints, tests and run docs.
- `contrib/pallavi-transcription-docker`: benchmark Whisper vs AI4Bharat IndicConformer, then selected transcription container and tests.

PR checklist: tests pass; no secrets/private audio; artifact version and license documented; API/error contract documented; note any changed TBD; preserve `RIAS HIGH → SUSPICIOUS`.

After creating an empty remote:
```bash
git remote add origin <REMOTE_URL>
git push -u origin main
git push origin contrib/project-lead-cfic
git push origin contrib/varun-pellav2-quantization
git push origin contrib/varshu-pellav2-docker
git push origin contrib/pallavi-transcription-docker
```
