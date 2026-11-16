# The kiosk app (Objective 5, Steps 4-5)

The backend (`server.py`, `service.py`, `config.py`, `model_server.py`) and the frontend (`static/`) of the kiosk.
The app runs turns through `kiosk_core`, the engine the harness evaluates. Everything stays local: Python's
standard library serves the app (no web framework to install), and the frontend is plain JavaScript with no build
step and no network access.

## 1. Try it with no model (stand-in mode)

```
python app\server.py --fake --open
```
This starts the stand-in llama-server (`harness/fake_server.py --demo`) and the stand-in retrieval. Replies are
canned: they quote the tool results or the store information the kiosk was shown. The routing, harness tools,
cards, drawers, compare mode and stage logs are the real code. Things to try:

1. "Formal watch for my father under 15000": product cards with quick replies. Open **Stages** and **Tool calls**.
2. "Do you offer gift wrapping?": a store question with a retrieval stage in the waterfall.
3. "Do you sell Fossil watches?": the entity check's fixed reply with real catalogue matches.
4. Pipeline, then Custom: turn Retrieval off. The banner says *untested*, and the next store question has no
   retrieval stage.
5. **Compare**: the same question to O3-final and to Model only, side by side.
6. Kiosk mode: `python app\server.py --fake --mode kiosk`. Only the chat is shown, and the configuration is fixed.

## 2. With the real models (on the laptop)

The app starts llama-server itself, with the plans' own settings. It uses `llama-cpu\` for Tier A and
`llama-vulkan\` for Tier B, and the model files under `models\`, all in the folder above the project (the plans'
`base_dir`). Stop any llama-server already running on port 8080 first.

```
python app\server.py --open                     # Lab mode, starts on Tier A (2B on CPU)
python app\server.py --mode kiosk --tier A      # Kiosk mode, Tier A
python app\server.py --mode kiosk --tier B      # Kiosk mode, Tier B (4B on Vulkan)
```
- At start-up the app loads the model and the retrieval models and sends the warm-up request, in the background
  (about 10-60 s); the page shows *Getting ready* and holds the input until it is done. In Kiosk mode a watchdog
  reloads llama-server if it ever stops. `--no-preload` restores loading on the first message.
- Changing tier or model swaps llama-server, and the chat shows the load time. Changing the pipeline only changes
  the turn settings.
- **Adapters:** once Objective 4, Step 5 has written `finetune\adapters_gguf\lora_2b.gguf` and the others, the
  Adapter chip offers them. Every adapter of the model is loaded at scale 0, and each request sets the scales, so
  switching costs no reload.
- **Logs:** `logs\app\<date>\<session>.jsonl` holds one turn record per line in the harness format, with stages.
  `logs\server\llama-server.log` is the server's own log.
- Use `--llama-port` if 8080 is taken, and `--port` to serve the app on another port than 8000.

## Step 4 with the real models

With the app running in Lab mode (`python app\server.py`), in a second terminal:
```
python app\smoke_real.py --tier A
python app\smoke_real.py --tier B
```
It runs design scenarios 1-5 through the API and checks replies, stages, cards and the brand placeholder. Report:
`results_obj5\_app_step4\smoke_<tier>.md`. Scenario 6 (Kiosk mode) is checked by hand.

## Step 5: accessibility scan

```
python app\a11y_check.py
```
Drives the app (stand-in model) through every scenario state in Lab and Kiosk mode and scans each: names, labels,
colour contrast, ARIA, duplicate ids, and a visible focus at every keyboard stop. It uses axe-core when installed
(`pip install axe-playwright-python`), otherwise its built-in checks. Report: `results_obj5\_a11y_step5\report.md`.

## Step 8: measurement

`python app\measure.py --tier A --policy resident --subset dev` starts the app itself, runs the speed subset through
the app and through the harness engine alternately, and stops everything at the end. See the file's header for the
full sequence (both Tier A policies, `--choose`, then one O3-T run per tier). Report:
`results_obj5\_measure_step8\report.md`.

## 3. Automated tests

```
python -m unittest app.test_app -v          # API (Lab and Kiosk) and the browser scenarios, stand-in model
python -m unittest kiosk_core.test_core -v  # the engine, stages, sequential policy
```
The browser tests need Playwright with Chromium (`pip install playwright` then `playwright install chromium`), and
are skipped without it.

## Notes

- **Turns run one at a time.** Compare mode runs side A, then side B, so two models never share RAM.
- **Brand placeholder.** The fictional brand's name never reaches the browser. `service.brand()` replaces it with
  ◇ ◇ ◇ in every event and response, while records and logs keep the data unchanged.
- **Evidence notes** next to each picker choice come from `app/evidence.json`, written from the Objectives doc;
  edit it as results come in.
- **Streaming:** replies appear word by word (Step 4's check found streamed and plain replies identical, so every
  round streams). Tool-call markup and half words are never shown, and the checked reply replaces the streamed
  text at the end. `--no-stream` shows each reply only when complete.
- **Product pictures (Step 7):** every card shows its watch's main picture, and "can I see the back of 1546SL01?"
  (or "iski photo dikhao" after a watch) opens all three views. Pictures come only from the media table
  (`python kiosk_core\media.py build` makes it), never from model text, and any URL a model writes is removed.
  They are drawn from each watch's attributes until the company's photos arrive.
- **Not built yet:** voice (the mic is disabled; `/api/voice/*` return 501).
