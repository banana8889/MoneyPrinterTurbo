# STARWOOD real generation attempt — 2026-10-25

## Actual video produced and inspected
Engine: OpenCV + FFmpeg on CPU, original procedural animation — NOT a generative AI model.
Output: six-second original forest sky/cold-open animation (internal rejected diagnostic).

| Metric | New render | Previous video |
|---|---:|---:|
| Duration | 6.000 s | 2.000 s |
| Resolution | 1280x720 | 640x360 |
| FPS | 24 | 24 |
| Decoded frames | 144 | 48 |
| Grayscale sampled frame delta (0-255) | 0.180 | 11.631 |
| Near-identical sampled adjacent frames | 97.1% | 0.0% |
| Average luma | 30.3 | 72.3 |

Result: REJECTED. Motion too static; original actor performances and audio missing. Not a film preview, no model inference and no reason to publish the clip.

## Execution environment
No NVIDIA GPU; nvidia-smi unavailable; torch CUDA unavailable; no cached video-model weights; GitHub and HuggingFace DNS from container unavailable. Cannot run Kandinsky 6, Wan 2.2, SVI or Helios model inference in this container.
One-off GitHub Actions workflow was committed on dev branch. No workflow run observed yet. Free standard GitHub Actions runner cannot be treated as an NVIDIA GPU machine.

## Next acceptance gate
Only genuine original AI video inference with licensed weights, stable original characters, visible body movement, synchronized distinct natural dialogue and independent viewing critique counts as a model trial.
Use studio/open_source_video_compare.py for technical QA, followed by human cinematic review. No paid service, no scheduled tasks, no change to main, do not show substandard partial movies.
