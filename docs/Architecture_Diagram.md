# BlendiOS — Architecture Diagrams

This document contains text-based architecture diagrams for BlendiOS. These diagrams are suitable for Markdown, documentation, and architecture review sessions.

---

## 1. High-Level System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Host Operating System                            │
│                     (Linux / macOS / Windows)                                 │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                            BlendiOS Environment                         │ │
│  │                                                                         │ │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐  │ │
│  │   │  Desktop     │   │  FastAPI     │   │  Streamlit               │  │ │
│  │   │  Shell       │   │  Backend     │   │  Dashboard               │  │ │
│  │   │  (PySide6)   │   │  (REST API)  │   │  (Analytics)             │  │ │
│  │   └──────┬───────┘   └──────┬───────┘   └────────────┬─────────────┘  │ │
│  │          │                  │                        │                │ │
│  │          └──────────────────┼────────────────────────┘                │ │
│  │                             │                                         │ │
│  │   ┌─────────────────────────▼─────────────────────────────────────┐   │ │
│  │   │                         Kernel                                 │   │ │
│  │   │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐  │   │ │
│  │   │  │ Process    │ │ Scheduler  │ │ Memory     │ │ Service   │  │   │ │
│  │   │  │ Manager    │ │            │ │ Manager    │ │ Manager   │  │   │ │
│  │   │  └────────────┘ └────────────┘ └────────────┘ └───────────┘  │   │ │
│  │   │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐  │   │ │
│  │   │  │ Crash      │ │ Event Bus  │ │ Window     │ │ Plugin    │  │   │ │
│  │   │  │ Handler    │ │            │ │ Manager    │ │ Loader    │  │   │ │
│  │   │  └────────────┘ └────────────┘ └────────────┘ └───────────┘  │   │ │
│  │   └──────────────────────────────────────────────────────────────┘   │ │
│  │                              │                                        │ │
│  │   ┌──────────────────────────┼───────────────────────────────────┐  │ │
│  │   │          Subsystems        │                                   │  │ │
│  │   │  ┌───────────┐  ┌─────────┴────┐  ┌──────────┐  ┌─────────┐ │  │ │
│  │   │  │ Users &   │  │ Virtual File │  │ Database │  │ Themes  │ │  │ │
│  │   │  │ Security  │  │ System       │  │ (SQLite) │  │ Engine  │ │  │ │
│  │   │  └───────────┘  └──────────────┘  └──────────┘  └─────────┘ │  │ │
│  │   └──────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │   ┌────────────────────────────────────────────────────────────────┐   │ │
│  │   │                     Applications Layer                          │   │ │
│  │   │  File  │ Terminal │ Settings │ Calc │ Notes │ Browser │ Media  │   │ │
│  │   │  Paint │ TaskMgr  │ AppStore │ ...  │       │         │        │   │ │
│  │   └────────────────────────────────────────────────────────────────┘   │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Presentation / UI                                     │
│  Desktop Shell • Apps • Widgets • Notifications • Themes        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: API & Integration                                     │
│  FastAPI Routers • REST Clients • Streamlit Dashboard           │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Application Services                                  │
│  Window Manager • App Registry • Search • Plugin Engine         │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Kernel / Core OS Simulation                           │
│  Process Manager • Scheduler • Memory Manager • Service Manager │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Infrastructure & Persistence                          │
│  VFS • SQLite • Security • Encryption • Logging • Config        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Kernel Internal Flow

```
                    ┌─────────────────┐
                    │   App Launch    │
                    │    Request      │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      Process Manager         │
              │  create_process(app_id, ...) │
              └──────────────┬───────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌──────────┐  ┌──────────┐  ┌──────────────┐
       │ Scheduler│  │ Memory   │  │ Event Bus    │
       │ enqueue  │  │ allocate │  │ publish      │
       └────┬─────┘  └────┬─────┘  └──────┬───────┘
            │             │               │
            ▼             ▼               ▼
       ┌─────────────────────────────────────────┐
       │         Desktop / Window Manager        │
       │   Open window, update taskbar, focus    │
       └─────────────────────────────────────────┘
```

---

## 4. Security & Authentication Flow

```
User
 │
 │ POST /auth/login
 │ {username, password}
 ▼
┌─────────────────┐
│   Auth Service  │
│  bcrypt.verify  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     No     ┌─────────────────┐
│ Valid Password? │───────────►│  Audit Logger   │
└────────┬────────┘            │  Failed Login   │
         │ Yes                 └─────────────────┘
         ▼
┌─────────────────┐
│ Session Manager │
│  create_token   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Return Tokens  │
│ access + refresh│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  Subsequent Requests: Bearer <access_token> │
│  ──► Token Validation ──► Permission Check  │
│  ──► Resource Access  ──► Audit Logger      │
└─────────────────────────────────────────────┘
```

---

## 5. Virtual File System Data Flow

```
App / Terminal / API
         │
         ▼
┌───────────────────────┐
│   VirtualFileSystem   │
│   (vfs.py)            │
└───────────┬───────────┘
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
┌───────┐ ┌───────┐ ┌───────────────┐
│ Folder│ │ File  │ │ Search Engine │
└───┬───┘ └───┬───┘ └───────┬───────┘
    │         │             │
    ▼         ▼             ▼
┌───────────────────────────────────────┐
│  Host filesystem (encrypted/compressed│
│  inside ~/.blendios/vfs/)             │
└───────────────────────────────────────┘
```

---

## 6. Plugin Extension Model

```
┌──────────────────────────────────────────────┐
│              Plugin Directory                 │
│   ~/.blendios/plugins/                        │
│   └── MyPlugin/plugin.json                    │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
            ┌───────────────────┐
            │   Plugin Loader   │
            │  validate + import│
            └─────────┬─────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌───────────┐
   │  Apps   │  │ Widgets │  │ Commands  │
   │Registry │  │Registry │  │Registry   │
   └────┬────┘  └────┬────┘  └─────┬─────┘
        │            │             │
        └────────────┼─────────────┘
                     ▼
            ┌─────────────────┐
            │   BlendiOS UI   │
            │  + Kernel + API │
            └─────────────────┘
```

---

## 7. Data Flow for Dashboard

```
┌─────────────────┐      HTTP GET       ┌─────────────────┐
│   Streamlit     │ ◄─────────────────► │    FastAPI      │
│   Dashboard     │  poll /system/status│    Backend      │
└─────────────────┘                     └────────┬────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
            ┌─────────────┐             ┌─────────────┐               ┌─────────────┐
            │   Kernel    │             │   SQLite    │               │     VFS     │
            │  CPU / RAM  │             │  Users/Logs │               │   Storage   │
            └─────────────┘             └─────────────┘               └─────────────┘
```

---

## 8. Application Launch Sequence

```
User clicks app icon
        │
        ▼
┌───────────────┐
│ Desktop Shell │
└───────┬───────┘
        │ launch_app(app_id)
        ▼
┌───────────────┐
│     Kernel    │
│ ProcessManager│
└───────┬───────┘
        │ create_process()
        ▼
┌───────────────┐
│  App Registry │
│ create_instance│
└───────┬───────┘
        │
        ▼
┌───────────────┐
│   BaseApp     │
│  build UI     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│Window Manager │
│ create_window │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  ManagedWindow│
│  shown on UI  │
└───────────────┘
```

---

## 9. Memory Manager Block Diagram

```
Total Simulated RAM: 4 GB
┌────────────────────────────────────────────────────────────┐
│  Kernel Reserved    │ 256 MB                                │
├────────────────────────────────────────────────────────────┤
│  Process A          │ 512 MB  [allocated]                   │
├────────────────────────────────────────────────────────────┤
│  Free Block         │ 1 GB    [first-fit / best-fit]        │
├────────────────────────────────────────────────────────────┤
│  Process B          │ 768 MB  [allocated]                   │
├────────────────────────────────────────────────────────────┤
│  Free Block         │ 512 MB                                │
├────────────────────────────────────────────────────────────┤
│  Process C          │ 256 MB  [allocated]                   │
├────────────────────────────────────────────────────────────┤
│  Free Block         │ 768 MB                                │
└────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Page Table         │
│  Virtual ► Physical │
└─────────────────────┘
```

---

## 10. Scheduler Comparison Diagram

```
Processes: P1(10ms), P2(4ms), P3(2ms), P4(6ms)

FIFO:
├──────────┬──────┬──────┬────────┤
│    P1    │  P2  │  P3  │   P4   │
0         10     14     16       22

Round Robin (quantum=4):
├──────┬──────┬──────┬──────┬──────┬──────┤
│  P1  │  P2  │  P3  │  P4  │  P1  │  P4  │  P1
0      4      8     10     14     18     20     22

Priority (lower = higher):
P3(1) ► P2(2) ► P4(3) ► P1(4)

SJF:
P3(2) ► P2(4) ► P4(6) ► P1(10)
```

---

*End of Architecture Diagrams*
