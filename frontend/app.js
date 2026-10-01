"use strict";

// SSE is a sequence of lines, not network chunks. Retain incomplete lines,
// including a trailing CR that might be the first half of a CRLF delimiter.
function createSseParser(onEvent) {
  let buffer = "";
  let eventName = "";
  let dataLines = [];
  function acceptLine(line) {
    if (line === "") {
      const event = { type: eventName || "message", data: dataLines.join("\n") };
      const hasData = dataLines.length > 0;
      eventName = "";
      dataLines = [];
      if (hasData) onEvent(event);
      return;
    }
    if (line.startsWith(":")) return;
    const colon = line.indexOf(":");
    const field = colon < 0 ? line : line.slice(0, colon);
    let value = colon < 0 ? "" : line.slice(colon + 1);
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") eventName = value;
    if (field === "data") dataLines.push(value);
    // id/retry and unknown fields are irrelevant to this one-shot POST stream.
  }
  return {
    feed(text, endOfStream = false) {
      buffer += text;
      let start = 0;
      for (let index = 0; index < buffer.length; index++) {
        const char = buffer[index];
        if (char !== "\r" && char !== "\n") continue;
        if (char === "\r" && index === buffer.length - 1 && !endOfStream) break;
        acceptLine(buffer.slice(start, index));
        if (char === "\r" && buffer[index + 1] === "\n") index++;
        start = index + 1;
      }
      buffer = buffer.slice(start);
      // EOF never dispatches a record without its terminating blank line.
    },
  };
}

class ResearchError extends Error {}
const unreadableResponse = () => new ResearchError(
  "The research service returned an unreadable response. Please try again."
);
const isRecord = (value) => value !== null && typeof value === "object" && !Array.isArray(value);
const nullableString = (value) => value === null || typeof value === "string";

function parseSseEvent(event) {
  if (!["status", "token", "sources", "done", "error"].includes(event.type)) return null;
  if (event.type === "error") {
    // Never expose backend exception messages or details.
    throw new ResearchError("We couldn't complete this research request. Please try again.");
  }
  let data;
  try { data = JSON.parse(event.data); } catch { throw unreadableResponse(); }
  if (!isRecord(data)) throw unreadableResponse();
  if (event.type === "status" && typeof data.message !== "string") throw unreadableResponse();
  if (event.type === "token" && typeof data.text !== "string") throw unreadableResponse();
  if (event.type === "sources") {
    const validCorpus = (source) => isRecord(source) && Number.isInteger(source.number)
      && typeof source.book_id === "string" && typeof source.text === "string"
      && nullableString(source.chapter) && nullableString(source.section);
    const validWeb = (source) => isRecord(source) && Number.isInteger(source.number)
      && typeof source.title === "string" && typeof source.url === "string";
    if (!Array.isArray(data.corpus_sources) || !data.corpus_sources.every(validCorpus)
      || !Array.isArray(data.web_sources) || !data.web_sources.every(validWeb)) throw unreadableResponse();
  }
  return { type: event.type, data };
}

async function consumeSseStream(response, signal, onEvent) {
  if (!response.ok) {
    throw new ResearchError(response.status === 429
      ? "The research service is busy. Please wait a moment and try again."
      : "The research service could not start this request. Please try again.");
  }
  if (!response.body || !response.headers.get("content-type")?.includes("text/event-stream")) {
    throw unreadableResponse();
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let complete = false;
  const parser = createSseParser((record) => {
    if (complete || signal.aborted) return;
    const event = parseSseEvent(record);
    if (!event) return;
    if (event.type === "done") complete = true;
    onEvent(event);
  });
  try {
    while (!complete) {
      const chunk = await reader.read();
      if (signal.aborted) throw new DOMException("Aborted", "AbortError");
      parser.feed(chunk.done ? decoder.decode() : decoder.decode(chunk.value, { stream: true }), chunk.done);
      if (chunk.done) break;
    }
    if (!complete) throw new ResearchError("The connection ended before research finished. Please try again.");
  } finally {
    try { await reader.cancel(); } catch { /* The connection may already be closed. */ }
    reader.releaseLock();
  }
}

const ui = Object.fromEntries([
  "landing", "research-form", "query", "submit-button", "result", "question-heading",
  "status", "status-mark", "status-text", "error-notice", "error-message", "retry",
  "answer-section", "answer-placeholder", "answer", "writing-mark", "sources",
  "source-count", "corpus-group", "corpus-sources", "web-group", "web-sources",
  "reading-note", "new-research",
].map((id) => [id, document.getElementById(id)]));

const state = { query: "", answer: "", isStreaming: false };
let activeRequest = null;
const answerText = document.createTextNode("");
ui.answer.append(answerText);

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderStatus(message, active, failed = false) {
  ui["status-text"].textContent = message;
  ui["status-mark"].classList.toggle("spinning", active);
  ui["status-mark"].textContent = active ? "" : failed ? "!" : "✓";
  ui["answer-section"].setAttribute("aria-busy", String(active));
  ui["writing-mark"].hidden = !active || !state.answer;
}

function appendAnswer(text) {
  state.answer += text;
  answerText.data = state.answer; // One text node for the entire answer.
  ui.answer.hidden = !state.answer;
  ui["answer-placeholder"].hidden = Boolean(state.answer);
  ui["writing-mark"].hidden = !state.isStreaming || !state.answer;
}

const bookTitles = Object.freeze({
  crime_and_punishment: "Crime and Punishment",
  brothers_karamazov: "The Brothers Karamazov",
  notes_from_underground: "Notes from Underground",
  demons: "Demons",
  idiot: "The Idiot",
});

function renderCorpusSources(sources) {
  const fragment = document.createDocumentFragment();
  sources.forEach((source) => {
    const title = Object.hasOwn(bookTitles, source.book_id) ? bookTitles[source.book_id]
      : source.book_id.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
    const details = element("details", "corpus-source");
    const summary = element("summary");
    const info = element("span", "source-info");
    info.append(element("strong", "", title));
    const metadata = [
      source.chapter && "Chapter " + source.chapter,
      source.section && "Section " + source.section,
    ].filter(Boolean).join(" · ");
    if (metadata) info.append(element("span", "source-meta", metadata));
    const icon = element("span", "expand-icon", "+");
    icon.setAttribute("aria-hidden", "true");
    summary.append(element("span", "source-number", "[" + source.number + "]"), info,
      element("span", "passage-label", "Read passage"), icon);
    const passage = element("div", "source-passage", source.text);
    passage.tabIndex = 0;
    passage.setAttribute("role", "region");
    passage.setAttribute("aria-label", "Passage from " + title);
    details.append(summary, passage);
    fragment.append(details);
  });
  ui["corpus-sources"].replaceChildren(fragment);
  ui["corpus-group"].hidden = sources.length === 0;
}

function renderWebSources(sources) {
  const fragment = document.createDocumentFragment();
  sources.forEach((source) => {
    const row = element("li");
    const info = element("div");
    let url;
    try {
      const candidate = new URL(source.url);
      if (["https:", "http:"].includes(candidate.protocol)) url = candidate;
    } catch { /* Invalid URLs are displayed as text, never as active links. */ }
    if (url) {
      const link = element("a", "", source.title || url.hostname);
      link.href = url.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      const arrow = element("span", "", " ↗");
      arrow.setAttribute("aria-hidden", "true");
      link.append(arrow, element("span", "sr-only", " (opens in a new tab)"));
      info.append(link, element("span", "source-domain", url.hostname));
    } else {
      info.append(element("span", "", source.title || "External reference"));
    }
    row.append(element("span", "source-number", "[" + source.number + "]"), info);
    fragment.append(row);
  });
  ui["web-sources"].replaceChildren(fragment);
  ui["web-group"].hidden = sources.length === 0;
}

function renderSources(corpusSources, webSources) {
  renderCorpusSources(corpusSources);
  renderWebSources(webSources);
  const count = corpusSources.length + webSources.length;
  ui.sources.hidden = count === 0;
  ui["source-count"].textContent = count + (count === 1 ? " reference" : " references");
}

function handleSseEvent(event) {
  switch (event.type) {
    case "status": renderStatus(event.data.message, true); break;
    case "token": appendAnswer(event.data.text); break;
    case "sources": renderSources(event.data.corpus_sources, event.data.web_sources); break;
    case "done":
      state.isStreaming = false;
      renderStatus("Research complete", false);
      ui["answer-placeholder"].hidden = true;
      if (!state.answer) {
        ui.answer.hidden = false;
        answerText.data = "No answer was returned. Start a new research query to try again.";
      }
      ui["reading-note"].hidden = false;
      break;
  }
}

function showError(error) {
  state.isStreaming = false;
  renderStatus("Research interrupted", false, true);
  ui["answer-placeholder"].hidden = true;
  ui["error-message"].textContent = (error instanceof ResearchError ? error.message
    : "Unable to connect to the research service. Please check your connection and try again.")
    + (state.answer ? " The partial answer below may be incomplete." : "");
  ui["error-notice"].hidden = false;
}

async function submitResearch(question) {
  if (activeRequest || !question.trim()) return;
  const controller = new AbortController();
  activeRequest = controller;
  state.query = question.trim();
  state.answer = "";
  state.isStreaming = true;
  ui["submit-button"].disabled = true;
  ui.retry.disabled = true;
  ui.landing.hidden = true;
  ui.result.hidden = false;
  ui["question-heading"].textContent = state.query;
  ui["error-notice"].hidden = true;
  ui["reading-note"].hidden = true;
  appendAnswer("");
  renderSources([], []);
  renderStatus("Analyzing your question...", true);
  ui["question-heading"].focus();

  try {
    const response = await fetch("/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({ message: state.query }),
      signal: controller.signal,
    });
    await consumeSseStream(response, controller.signal, (event) => {
      if (activeRequest === controller && !controller.signal.aborted) handleSseEvent(event);
    });
  } catch (error) {
    if (activeRequest === controller && !controller.signal.aborted) showError(error);
  } finally {
    if (activeRequest === controller) {
      activeRequest = null;
      state.isStreaming = false;
      ui.retry.disabled = false;
      ui["submit-button"].disabled = !ui.query.value.trim();
    }
  }
}

function resetResearch() {
  activeRequest?.abort();
  activeRequest = null;
  state.query = "";
  state.answer = "";
  state.isStreaming = false;
  answerText.data = "";
  renderSources([], []);
  ui.result.hidden = true;
  ui.landing.hidden = false;
  ui.query.value = "";
  ui["submit-button"].disabled = true;
  ui.query.focus();
}

ui["research-form"].addEventListener("submit", (event) => {
  event.preventDefault();
  void submitResearch(ui.query.value);
});
ui.query.addEventListener("input", () => {
  ui["submit-button"].disabled = Boolean(activeRequest) || !ui.query.value.trim();
});
ui.query.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey) && !event.isComposing) {
    event.preventDefault();
    ui["research-form"].requestSubmit();
  }
});
ui.retry.addEventListener("click", () => { void submitResearch(state.query); });
ui["new-research"].addEventListener("click", resetResearch);
document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => {
    ui.query.value = button.firstElementChild.textContent;
    ui["submit-button"].disabled = false;
    ui.query.focus();
  });
});
window.addEventListener("pagehide", () => { if (activeRequest) resetResearch(); });
