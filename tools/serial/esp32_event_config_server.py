#!/usr/bin/env python3
"""Serve a local web UI for editing esp32_event_control.json.

Usage:
  python3 tools/serial/esp32_event_config_server.py
  python3 tools/serial/esp32_event_config_server.py --port 8765
  python3 tools/serial/esp32_event_config_server.py --config custom.json
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import socket
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = SCRIPT_DIR / "esp32_event_control.json"


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ESP32 Event Config</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --line: #d8dde6;
      --text: #17202a;
      --muted: #5d6b7c;
      --accent: #1f7a5a;
      --accent-strong: #155f45;
      --danger: #b42318;
      --shadow: 0 1px 2px rgba(18, 26, 36, 0.08);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button, input, textarea, select {
      font: inherit;
    }

    button {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
      padding: 8px 11px;
      cursor: pointer;
      min-height: 36px;
    }

    button:hover { border-color: #aeb8c6; }
    button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
    button.primary:hover { background: var(--accent-strong); }
    button.danger { color: var(--danger); }
    button.icon { width: 36px; padding: 0; }

    .app {
      display: grid;
      grid-template-columns: 270px minmax(0, 1fr);
      min-height: 100vh;
    }

    aside {
      background: #eef1f5;
      border-right: 1px solid var(--line);
      padding: 16px;
    }

    main {
      padding: 18px 22px 28px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
    }

    h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 650;
      letter-spacing: 0;
    }

    h2 {
      margin: 0 0 10px;
      font-size: 15px;
      font-weight: 650;
      letter-spacing: 0;
    }

    .subtle {
      color: var(--muted);
      font-size: 12px;
    }

    .event-list {
      display: grid;
      gap: 6px;
      margin-top: 12px;
    }

    .event-button {
      width: 100%;
      text-align: left;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      background: transparent;
      border-color: transparent;
      padding: 8px 9px;
    }

    .event-button.active {
      background: #fff;
      border-color: var(--line);
      box-shadow: var(--shadow);
    }

    .event-name {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .count {
      color: var(--muted);
      font-size: 12px;
    }

    .add-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 36px;
      gap: 8px;
      margin-top: 14px;
    }

    input, textarea, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
      padding: 8px 10px;
      min-height: 36px;
    }

    input[type="color"] {
      height: 38px;
      padding: 3px;
    }

    input[readonly] {
      background: #f3f5f7;
      color: var(--muted);
    }

    textarea {
      min-height: 78px;
      resize: vertical;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      line-height: 1.4;
    }

    .section-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
      padding: 14px;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      margin-bottom: 12px;
    }

    .field {
      display: grid;
      gap: 6px;
      margin-bottom: 12px;
    }

    .param-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 12px;
    }

    .param-grid .wide {
      grid-column: 1 / -1;
    }

    label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 600;
    }

    .toggle {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
      user-select: none;
    }

    .toggle input {
      width: 16px;
      height: 16px;
      min-height: 16px;
      padding: 0;
    }

    .actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .raw-wrap {
      margin-top: 14px;
    }

    .status {
      min-height: 20px;
      color: var(--muted);
      font-size: 13px;
    }

    .status.error { color: var(--danger); }
    .status.ok { color: var(--accent-strong); }

    .hidden { display: none; }

    @media (max-width: 860px) {
      .app { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
      .section-grid { grid-template-columns: 1fr; }
      main { padding: 16px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div>
        <h1>ESP32 Events</h1>
        <div class="subtle" id="configPath"></div>
      </div>
      <div class="add-row">
        <input id="newEvent" placeholder="NewEventName" autocomplete="off">
        <button class="icon" id="addEvent" title="Add event">+</button>
      </div>
      <div class="event-list" id="eventList"></div>
    </aside>

    <main>
      <div class="topbar">
        <div>
          <h1 id="currentTitle">Select an event</h1>
          <div class="subtle">Use enums and typed fields. Saving writes the JSON file.</div>
        </div>
        <div class="actions">
          <button id="rawToggle">Raw JSON</button>
          <button class="danger" id="deleteEvent">Delete</button>
          <button class="primary" id="saveConfig">Save</button>
        </div>
      </div>

      <div class="status" id="status"></div>

      <div id="editor" class="section-grid"></div>

      <div class="raw-wrap hidden" id="rawWrap">
        <div class="panel">
          <div class="panel-header">
            <h2>Raw JSON</h2>
            <button id="applyRaw">Apply</button>
          </div>
          <textarea id="rawJson" spellcheck="false"></textarea>
        </div>
      </div>
    </main>
  </div>

  <script>
    const sections = [
      { key: "light", title: "Light", defaultCommand: ["yellow"] },
      { key: "buzzer", title: "Buzzer", defaultCommand: ["beep", "2000", "200"] },
      { key: "vibration", title: "Vibration", defaultCommand: ["vibrate", "500"] },
    ];

    const sectionOptions = {
      light: [
        ["off", "Off"],
        ["yellow", "Yellow breathing"],
        ["chase", "Chase"],
        ["alternate", "Alternate"],
        ["rainbow", "Rainbow"],
        ["auto", "Auto cycle"],
        ["solid", "Solid color"],
        ["on", "GPIO on"],
        ["blink", "GPIO blink"],
      ],
      buzzer: [
        ["beep", "Beep"],
        ["tone", "Continuous tone"],
        ["drop", "Water drop"],
        ["off", "Off"],
      ],
      vibration: [
        ["vibrate", "Vibrate"],
      ],
    };

    let config = { default: { light: { command: ["off"] } }, events: {} };
    let selectedEvent = "";
    let rawVisible = false;

    const eventList = document.getElementById("eventList");
    const editor = document.getElementById("editor");
    const statusEl = document.getElementById("status");
    const currentTitle = document.getElementById("currentTitle");
    const rawWrap = document.getElementById("rawWrap");
    const rawJson = document.getElementById("rawJson");

    function setStatus(text, kind = "") {
      statusEl.textContent = text;
      statusEl.className = "status" + (kind ? " " + kind : "");
    }

    function clampNumber(value, minimum, maximum, fallback) {
      const parsed = Number.parseInt(value, 10);
      if (Number.isNaN(parsed)) return fallback;
      return Math.min(Math.max(parsed, minimum), maximum);
    }

    function rgbToHex(r, g, b) {
      return [r, g, b]
        .map(value => clampNumber(value, 0, 255, 0).toString(16).padStart(2, "0"))
        .join("")
        .replace(/^/, "#");
    }

    function hexToRgb(hex) {
      const match = /^#?([0-9a-f]{6})$/i.exec(hex);
      const value = match ? match[1] : "ffff00";
      return [
        Number.parseInt(value.slice(0, 2), 16),
        Number.parseInt(value.slice(2, 4), 16),
        Number.parseInt(value.slice(4, 6), 16),
      ];
    }

    function commandName(command, fallback) {
      return Array.isArray(command) && command.length ? String(command[0]) : fallback;
    }

    function defaultCommandFor(sectionKey, mode) {
      if (sectionKey === "light") {
        if (mode === "solid") return ["solid", "255", "180", "0", "0"];
        return [mode || "yellow"];
      }
      if (sectionKey === "buzzer") {
        if (mode === "tone") return ["tone", "2000", "50"];
        if (mode === "drop") return ["drop", "1"];
        if (mode === "off") return ["buzzer", "off"];
        return ["beep", "2000", "200"];
      }
      return ["vibrate", "500"];
    }

    function sectionMode(sectionKey, command) {
      const name = commandName(command, "");
      if (sectionKey === "buzzer" && name === "buzzer") return command[1] === "off" ? "off" : "beep";
      if (sectionKey === "vibration") return "vibrate";
      return name || defaultCommandFor(sectionKey)[0];
    }

    function setSectionCommand(entry, sectionKey, command) {
      if (!entry[sectionKey]) entry[sectionKey] = {};
      entry[sectionKey].command = command.map(value => String(value));
    }

    function makeNumberField(labelText, value, minimum, maximum, onInput) {
      const field = document.createElement("div");
      field.className = "field";
      const label = document.createElement("label");
      label.textContent = labelText;
      const input = document.createElement("input");
      input.type = "number";
      input.min = String(minimum);
      input.max = String(maximum);
      input.value = String(value);
      input.addEventListener("input", () => onInput(clampNumber(input.value, minimum, maximum, value)));
      field.append(label, input);
      return field;
    }

    function makeColorField(labelText, value, onInput) {
      const field = document.createElement("div");
      field.className = "field wide";
      const label = document.createElement("label");
      label.textContent = labelText;
      const input = document.createElement("input");
      input.type = "color";
      input.value = value;
      input.addEventListener("input", () => onInput(input.value));
      field.append(label, input);
      return field;
    }

    function renderParameterControls(sectionKey, params, entry, refreshCommandText) {
      const command = entry[sectionKey]?.command || defaultCommandFor(sectionKey);
      const mode = sectionMode(sectionKey, command);
      params.innerHTML = "";

      if (sectionKey === "light" && mode === "solid") {
        let rgb = [
          clampNumber(command[1], 0, 255, 255),
          clampNumber(command[2], 0, 255, 180),
          clampNumber(command[3], 0, 255, 0),
        ];
        let beepMs = clampNumber(command[4], 0, 10000, 0);
        const update = () => {
          setSectionCommand(entry, sectionKey, ["solid", ...rgb, beepMs]);
          refreshCommandText();
        };
        params.append(
          makeColorField("Color", rgbToHex(...rgb), value => {
            rgb = hexToRgb(value);
            update();
          }),
          makeNumberField("Optional beep ms", beepMs, 0, 10000, value => {
            beepMs = value;
            update();
          })
        );
      }

      if (sectionKey === "buzzer" && mode === "beep") {
        let frequency = clampNumber(command[1], 20, 20000, 2000);
        let duration = clampNumber(command[2], 10, 10000, 200);
        const update = () => {
          setSectionCommand(entry, sectionKey, ["beep", frequency, duration]);
          refreshCommandText();
        };
        params.append(
          makeNumberField("Frequency Hz", frequency, 20, 20000, value => {
            frequency = value;
            update();
          }),
          makeNumberField("Duration ms", duration, 10, 10000, value => {
            duration = value;
            update();
          })
        );
      }

      if (sectionKey === "buzzer" && mode === "tone") {
        let frequency = clampNumber(command[1], 20, 20000, 2000);
        let duty = clampNumber(command[2], 1, 90, 50);
        const update = () => {
          setSectionCommand(entry, sectionKey, ["tone", frequency, duty]);
          refreshCommandText();
        };
        params.append(
          makeNumberField("Frequency Hz", frequency, 20, 20000, value => {
            frequency = value;
            update();
          }),
          makeNumberField("Duty percent", duty, 1, 90, value => {
            duty = value;
            update();
          })
        );
      }

      if (sectionKey === "buzzer" && mode === "drop") {
        let count = clampNumber(command[1], 1, 10, 1);
        params.append(makeNumberField("Repeat count", count, 1, 10, value => {
          count = value;
          setSectionCommand(entry, sectionKey, ["drop", count]);
          refreshCommandText();
        }));
      }

      if (sectionKey === "vibration") {
        let duration = clampNumber(command[1], 1, 60000, 500);
        params.append(makeNumberField("Duration ms", duration, 1, 60000, value => {
          duration = value;
          setSectionCommand(entry, sectionKey, ["vibrate", duration]);
          refreshCommandText();
        }));
      }
    }

    function ensureEvent(name) {
      if (!config.events) config.events = {};
      if (!config.events[name]) config.events[name] = {};
      return config.events[name];
    }

    function sectionCount(entry) {
      return sections.filter(section => entry && entry[section.key]).length;
    }

    function renderEvents() {
      const names = Object.keys(config.events || {}).sort();
      eventList.innerHTML = "";
      if (!selectedEvent && names.length) selectedEvent = names[0];
      if (selectedEvent && !config.events[selectedEvent]) selectedEvent = names[0] || "";

      for (const name of names) {
        const button = document.createElement("button");
        button.className = "event-button" + (name === selectedEvent ? " active" : "");
        button.innerHTML = `<span class="event-name"></span><span class="count"></span>`;
        button.querySelector(".event-name").textContent = name;
        button.querySelector(".count").textContent = sectionCount(config.events[name]);
        button.addEventListener("click", () => {
          selectedEvent = name;
          render();
        });
        eventList.appendChild(button);
      }
    }

    function renderEditor() {
      editor.innerHTML = "";
      if (!selectedEvent) {
        currentTitle.textContent = "Select an event";
        return;
      }

      currentTitle.textContent = selectedEvent;
      const entry = ensureEvent(selectedEvent);
      for (const section of sections) {
        const value = entry[section.key] || {};
        const enabled = Boolean(entry[section.key]);
        const mode = sectionMode(section.key, value.command);
        const panel = document.createElement("section");
        panel.className = "panel";
        panel.innerHTML = `
          <div class="panel-header">
            <h2>${section.title}</h2>
            <label class="toggle">
              <input type="checkbox" ${enabled ? "checked" : ""}>
              enabled
            </label>
          </div>
          <div class="field">
            <label>Mode</label>
            <select class="mode"></select>
          </div>
          <div class="param-grid"></div>
          <div class="field">
            <label>Generated command</label>
            <input class="command" readonly>
          </div>
          <div class="field">
            <label>Description</label>
            <textarea class="description" placeholder="${section.title} note"></textarea>
          </div>
        `;

        const checkbox = panel.querySelector("input[type=checkbox]");
        const modeSelect = panel.querySelector(".mode");
        const params = panel.querySelector(".param-grid");
        const command = panel.querySelector(".command");
        const description = panel.querySelector(".description");

        for (const [optionValue, label] of sectionOptions[section.key]) {
          const option = document.createElement("option");
          option.value = optionValue;
          option.textContent = label;
          modeSelect.appendChild(option);
        }
        modeSelect.value = mode;

        const refreshCommandText = () => {
          command.value = (entry[section.key]?.command || []).join(" ");
          renderRaw();
        };

        if (enabled) {
          renderParameterControls(section.key, params, entry, refreshCommandText);
        }
        refreshCommandText();
        description.value = value.description || "";
        modeSelect.disabled = !enabled;
        command.disabled = !enabled;
        description.disabled = !enabled;

        checkbox.addEventListener("change", () => {
          if (checkbox.checked) {
            entry[section.key] = { command: defaultCommandFor(section.key, modeSelect.value) };
            if (description.value.trim()) entry[section.key].description = description.value.trim();
          } else {
            delete entry[section.key];
          }
          render();
        });

        modeSelect.addEventListener("change", () => {
          if (!entry[section.key]) return;
          setSectionCommand(entry, section.key, defaultCommandFor(section.key, modeSelect.value));
          render();
        });

        description.addEventListener("input", () => {
          if (!entry[section.key]) return;
          const text = description.value.trim();
          if (text) entry[section.key].description = text;
          else delete entry[section.key].description;
          renderRaw();
        });

        editor.appendChild(panel);
      }
    }

    function renderRaw() {
      rawJson.value = JSON.stringify(config, null, 2);
      rawWrap.classList.toggle("hidden", !rawVisible);
    }

    function render() {
      renderEvents();
      renderEditor();
      renderRaw();
    }

    async function loadConfig() {
      const response = await fetch("/api/config");
      if (!response.ok) throw new Error(await response.text());
      const payload = await response.json();
      config = payload.config;
      document.getElementById("configPath").textContent = payload.path;
      render();
      setStatus("Loaded", "ok");
    }

    async function saveConfig() {
      const response = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      if (!response.ok) throw new Error(await response.text());
      setStatus("Saved", "ok");
    }

    document.getElementById("addEvent").addEventListener("click", () => {
      const input = document.getElementById("newEvent");
      const name = input.value.trim();
      if (!name) return setStatus("Enter an event name", "error");
      if (!config.events) config.events = {};
      if (config.events[name]) return setStatus("Event already exists", "error");
      config.events[name] = { light: { command: ["yellow"] } };
      input.value = "";
      selectedEvent = name;
      render();
      setStatus("Event added");
    });

    document.getElementById("deleteEvent").addEventListener("click", () => {
      if (!selectedEvent) return;
      if (!confirm(`Delete ${selectedEvent}?`)) return;
      delete config.events[selectedEvent];
      selectedEvent = "";
      render();
      setStatus("Event deleted");
    });

    document.getElementById("saveConfig").addEventListener("click", () => {
      saveConfig().catch(error => setStatus(error.message, "error"));
    });

    document.getElementById("rawToggle").addEventListener("click", () => {
      rawVisible = !rawVisible;
      renderRaw();
    });

    document.getElementById("applyRaw").addEventListener("click", () => {
      try {
        const next = JSON.parse(rawJson.value);
        if (!next || typeof next !== "object" || Array.isArray(next)) throw new Error("Root must be an object");
        if (!next.events || typeof next.events !== "object" || Array.isArray(next.events)) {
          throw new Error("events must be an object");
        }
        config = next;
        selectedEvent = Object.keys(config.events).sort()[0] || "";
        render();
        setStatus("Raw JSON applied");
      } catch (error) {
        setStatus(error.message, "error");
      }
    });

    loadConfig().catch(error => setStatus(error.message, "error"));
  </script>
</body>
</html>
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the ESP32 event config web editor.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Config JSON file to edit")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind; use 0 for any free port")
    return parser


def validate_config(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Root JSON value must be an object")
    events = data.get("events")
    if not isinstance(events, dict):
        raise ValueError("'events' must be an object")

    for event_name, entry in events.items():
        if not isinstance(event_name, str) or not event_name:
            raise ValueError("Event names must be non-empty strings")
        validate_entry(entry, f"events.{event_name}")

    if "default" in data:
        validate_entry(data["default"], "default")
    return data


def validate_entry(entry: Any, path: str) -> None:
    if not isinstance(entry, dict):
        raise ValueError(f"{path} must be an object")
    if "command" in entry:
        validate_command(entry["command"], f"{path}.command")
        return
    for section in ("light", "buzzer", "vibration"):
        if section in entry:
            section_entry = entry[section]
            if not isinstance(section_entry, dict):
                raise ValueError(f"{path}.{section} must be an object")
            validate_command(section_entry.get("command"), f"{path}.{section}.command")
            description = section_entry.get("description")
            if description is not None and not isinstance(description, str):
                raise ValueError(f"{path}.{section}.description must be a string")


def validate_command(command: Any, path: str) -> None:
    if not isinstance(command, list) or not command:
        raise ValueError(f"{path} must be a non-empty array")
    for item in command:
        if not isinstance(item, (str, int, float)):
            raise ValueError(f"{path} items must be strings or numbers")


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return validate_config(json.load(file))


def write_config(path: Path, data: dict[str, Any]) -> None:
    validate_config(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")


class ConfigHandler(BaseHTTPRequestHandler):
    config_path: Path

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/":
            self.send_bytes(INDEX_HTML.encode("utf-8"), "text/html; charset=utf-8")
            return
        if route == "/api/config":
            try:
                payload = {
                    "path": str(self.config_path),
                    "config": read_config(self.config_path),
                }
                self.send_json(payload)
            except Exception as exc:
                self.send_error_text(str(exc), HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self.send_error_text("Not found", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route != "/api/config":
            self.send_error_text("Not found", HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            write_config(self.config_path, data)
            self.send_json({"ok": True})
        except json.JSONDecodeError as exc:
            self.send_error_text(f"Invalid JSON: {exc}", HTTPStatus.BAD_REQUEST)
        except ValueError as exc:
            self.send_error_text(str(exc), HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self.send_error_text(str(exc), HTTPStatus.INTERNAL_SERVER_ERROR)

    def send_json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_bytes(body, "application/json; charset=utf-8")

    def send_error_text(self, text: str, status: HTTPStatus) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(text.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def send_bytes(self, body: bytes, content_type: str | None = None) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or mimetypes.guess_type(self.path)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(config_path: Path, host: str, port: int) -> None:
    ConfigHandler.config_path = config_path.resolve()
    server = ThreadingHTTPServer((host, port), ConfigHandler)
    actual_host, actual_port = server.server_address[:2]
    display_host = "127.0.0.1" if actual_host in ("0.0.0.0", "") else actual_host
    print(f"Serving {ConfigHandler.config_path}")
    print(f"Open http://{display_host}:{actual_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()


def port_is_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) != 0


def main() -> int:
    args = build_parser().parse_args()
    port = args.port
    if port != 0 and not port_is_available(args.host, port):
        port = 0
    serve(args.config, args.host, port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
