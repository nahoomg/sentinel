# Nahom Getachew — Motion Design Showreel (15s)

`showreel.mp4` — 1920×1080, 60 fps, H.264 + AAC, with a synced 120 BPM soundtrack.

Everything is procedural: each frame is a pure function of time (`draw(t)` in `index.html`), and the audio is synthesised to the same cut list.

| Time | Section | Techniques |
|---|---|---|
| 0–2s | Open | dot → line → timeline ruler, masked type reveal, colour flood |
| 2–4s | Kinetic type | MOVE / SHAPE / TIME / FEEL — staggered masks, echoes, stretch, elastic, iris wipe |
| 4–6s | Geometry | wave-driven circle↔square grid, camera push, spiral collapse |
| 6–8.5s | Particle sim | ~6k particles explode, assemble into "NAHOM", blown away with motion streaks |
| 8.5–10.5s | Realtime 3D | point-cloud sphere → torus morph with perspective, orbit rings |
| 10.5–12s | Shape / timing | polygon morphs with echo trails, live graph editor, squash & stretch |
| 12–13s | Montage | 1/8-note cards with glitch slices |
| 13–15s | Title | NAHOM GETACHEW reveal, decoded subtitle, letterbox close back to the opening dot |

## Rebuild

```sh
npm i playwright-core            # uses a local Chromium
python3 audio.py                 # → showreel.wav
node render.mjs frames 60        # → frames/f0000.png … f0899.png
ffmpeg -framerate 60 -i frames/f%04d.png -i showreel.wav \
  -c:v libx264 -pix_fmt yuv420p -crf 17 -preset slow -c:a aac -b:a 192k -shortest showreel.mp4
```

Open `index.html` in a browser for realtime playback (click to restart with sound).
Fonts: Unbounded and JetBrains Mono (SIL OFL, licences in `fonts/`).
