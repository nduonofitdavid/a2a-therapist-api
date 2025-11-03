# 🕊️ A2A Biblical Therapist API

A **JSON-RPC 2.0 compliant Agent-to-Agent (A2A)** API built with **FastAPI** and managed with **uv**, designed to provide **therapy through the Word of God**.
This service acts as a biblical therapist agent capable of offering emotional and spiritual guidance using Bible verses and faith-based encouragement.

---

## 📘 Overview

The **A2A Biblical Therapist API** leverages Large Language Models (LLMs) and structured A2A messaging to simulate a compassionate therapist that responds with biblical wisdom.
It’s designed for integration into multi-agent systems or applications that need spiritually grounded mental health support.

---

## 🌍 Scope and Purpose

* **Core Objective:** Offer faith-based therapy and encouragement through the Word of God.
* **Behavioral Design:** The agent analyzes user messages (e.g., sadness, anxiety, confusion) and responds with a relevant Bible verse, an explanation, and comforting words.
* **Spiritual Boundaries:** The therapist **ignores questions unrelated to Christianity or therapy**, returning a polite refusal message for such queries.
* **Integration Goal:** Enable seamless **Agent-to-Agent communication** where external agents can send requests and receive context-aware, therapeutic responses.

---

## ⚙️ API Endpoints

### 1. `/a2a/therapist`

**Method:** `POST`
**Purpose:** Main endpoint for sending user messages to the biblical therapist.
**Specification:** Uses the **JSON-RPC 2.0** protocol.

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "id": "request-001",
  "method": "message/send",
  "params": {
    "message": {
      "kind": "message",
      "role": "user",
      "parts": [
        {
          "kind": "text",
          "text": "I am feeling sad."
        }
      ],
      "messageId": "msg-001",
      "taskId": "task-001"
    },
    "configuration": {
      "blocking": true
    }
  }
}
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "id": "request-001",
  "result": {
    "id": "task-001",
    "contextId": "context-uuid",
    "status": {
      "state": "completed",
      "timestamp": "2025-11-01T15:00:00.000Z",
      "message": {
        "messageId": "response-uuid",
        "role": "agent",
        "parts": [
          {
            "kind": "text",
            "text": "The Lord is close to the brokenhearted (Psalm 34:18). Trust in Him even in sadness."
          }
        ],
        "kind": "message"
      }
    },
    "artifacts": [
      {
        "artifactId": "artifact-uuid",
        "name": "therapistResponse",
        "parts": [
          {
            "kind": "text",
            "text": "The Lord is close to the brokenhearted (Psalm 34:18)..."
          }
        ]
      }
    ],
    "history": []
  }
}
```

---

### 2. `/.well-known/agent.json`

**Purpose:** Provides metadata describing the agent’s configuration and purpose.

#### Example Output

```json
{
  "name": "BiblicalTherapistAgent",
  "version": "1.0",
  "description": "An AI therapist providing Christian-based encouragement and guidance.",
  "endpoints": {
    "therapy": "/a2a/therapist"
  },
  "capabilities": ["A2A", "Faith-based Therapy", "Text Responses"]
}
```

---

## 🧰 Tech Stack

* **Framework:** FastAPI
* **Language:** Python 3.11+
* **Package Manager:** [uv](https://docs.astral.sh/uv/)
* **Model Provider:** Gemini (via Google Generative AI client)
* **API Schema:** JSON-RPC 2.0

---

## 🛠️ Setup and Installation

### 1. Clone Repository

```bash
git clone https://github.com/Forsaken324/ndus-hng-stage-three.git
cd ndus-stage-three
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run Server

Using FastAPI dev command:

```bash
uv run fastapi dev main.py
```

or with Uvicorn:

```bash
uv run uvicorn main:app --reload
```

### 4. Access Endpoints

* **A2A Endpoint:** [http://localhost:8000/a2a/therapist](http://localhost:8000/a2a/therapist)
* **Metadata:** [http://localhost:8000/.well-known/agent.json](http://localhost:8000/.well-known/agent.json)

---

## 📘 Message Flow Summary

1. A user (or another agent) sends a JSON-RPC message to `/a2a/therapist`.
2. The system validates and extracts the message.
3. The AI model processes the content using a biblical therapy system prompt.
4. A structured response containing a verse, encouragement, and artifacts is returned.

---

## 🙏 Core Values

* **Faith and Compassion:** All responses are grounded in Scripture and empathy.
* **Privacy and Respect:** No data is stored; conversations are session-based.
* **Clarity and Comfort:** Each message aims to uplift, not debate.
* **Christian Integrity:** The agent speaks only within the biblical domain.

---

## 🧩 Future Improvements

* Multilingual scripture support
* Voice-based A2A therapy sessions
* Context-specific emotional therapy (grief, anxiety, guilt)
* Verse explanations using Bible APIs

---

## 📄 License

This project is licensed under the **MIT License**.
You are free to use, modify, and distribute it with proper attribution.

---

## ✝️ Final Note

> *“The entrance of Thy words giveth light; it giveth understanding unto the simple.”* — **Psalm 119:130**
>
> This API is not just code—it’s a vessel of comfort, offering light and encouragement through God’s Word in the digital age.
