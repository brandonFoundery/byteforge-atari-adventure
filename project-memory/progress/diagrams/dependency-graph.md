# Feature Dependency Graph

**Generated:** 2026-05-13

```mermaid
flowchart TD
    T1["Game Loop + Render Foundation"]:::done
    T2["Player Movement with Wall Collision"]:::done
    T3["Multi-Room World + Screen Transitions"]:::inprogress
    T1 -->|"T2 builds on T1"| T2
    T2 -->|"T3 builds on T2"| T3
    classDef done fill:#22c55e,color:#fff,stroke:#16a34a
    classDef inprogress fill:#3b82f6,color:#fff,stroke:#2563eb
    classDef planned fill:#f59e0b,color:#fff,stroke:#d97706
    classDef decision fill:#8b5cf6,color:#fff,stroke:#7c3aed
```
