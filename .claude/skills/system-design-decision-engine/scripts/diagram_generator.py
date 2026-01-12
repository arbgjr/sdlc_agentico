#!/usr/bin/env python3
"""
Mermaid Diagram Generator for System Design

Usage:
    python diagram_generator.py --list
    python diagram_generator.py --type basic
    python diagram_generator.py --type microservice --output arch.md
"""

import argparse
import sys

DIAGRAMS = {
    'basic': ('Basic Client-Server', '''```mermaid
graph TB
    Client[Client] --> LB[Load Balancer]
    LB --> S1[Server 1]
    LB --> S2[Server 2]
    S1 --> Cache[(Redis)]
    S2 --> Cache
    S1 --> DB[(Database)]
    S2 --> DB
```'''),

    'microservice': ('Microservices', '''```mermaid
graph TB
    Gateway[API Gateway] --> Auth[Auth Service]
    Gateway --> UserSvc[User Service]
    Gateway --> OrderSvc[Order Service]
    Gateway --> ProductSvc[Product Service]
    UserSvc --> UserDB[(User DB)]
    OrderSvc --> OrderDB[(Order DB)]
    OrderSvc --> Queue[(Message Queue)]
    ProductSvc --> ProductDB[(Product DB)]
    Queue --> NotifSvc[Notification Service]
```'''),

    'event-driven': ('Event-Driven', '''```mermaid
graph LR
    subgraph Producers
        P1[Order Service]
        P2[Payment Service]
    end
    subgraph "Event Bus"
        Kafka[Kafka]
    end
    subgraph Consumers
        C1[Analytics]
        C2[Notification]
        C3[Audit]
    end
    P1 --> Kafka
    P2 --> Kafka
    Kafka --> C1
    Kafka --> C2
    Kafka --> C3
```'''),

    'cqrs': ('CQRS Pattern', '''```mermaid
graph TB
    Client[Client]
    Client -->|commands| CmdAPI[Command API]
    Client -->|queries| QueryAPI[Query API]
    CmdAPI --> WriteDB[(Write DB)]
    CmdAPI --> EventStore[(Event Store)]
    EventStore --> EventBus[Event Bus]
    EventBus --> Projector[Projector]
    Projector --> ReadDB[(Read DB)]
    QueryAPI --> Cache[(Cache)]
    Cache -.->|miss| ReadDB
```'''),

    'cache': ('Caching Layers', '''```mermaid
graph TB
    Browser[Browser Cache] --> CDN[CDN]
    CDN --> LB[Load Balancer]
    LB --> App[App Server]
    App --> LocalCache[Local Cache]
    LocalCache --> Redis[(Redis)]
    Redis --> DB[(Database)]
```'''),

    'queue': ('Message Queue', '''```mermaid
graph LR
    API[API] --> Exchange[Exchange]
    Exchange --> Q1[Priority Queue]
    Exchange --> Q2[Normal Queue]
    Exchange --> DLQ[Dead Letter Queue]
    Q1 --> W1[Worker 1]
    Q2 --> W2[Worker 2]
    DLQ --> Retry[Retry Handler]
    W1 --> DB[(Database)]
    W2 --> DB
```'''),

    'database': ('DB Replication', '''```mermaid
graph TB
    App[Application] --> Pool[Connection Pool]
    Pool -->|writes| Primary[(Primary)]
    Pool -->|reads| R1[(Replica 1)]
    Pool -->|reads| R2[(Replica 2)]
    Primary -->|replication| R1
    Primary -->|replication| R2
    Primary -->|sync| Standby[(Standby)]
```'''),

    'saga': ('Saga Pattern', '''```mermaid
sequenceDiagram
    participant Client
    participant Orchestrator
    participant OrderSvc
    participant PaymentSvc
    participant InventorySvc

    Client->>Orchestrator: Create Order
    Orchestrator->>OrderSvc: 1. Create Order
    OrderSvc-->>Orchestrator: OK
    Orchestrator->>PaymentSvc: 2. Process Payment
    PaymentSvc-->>Orchestrator: OK
    Orchestrator->>InventorySvc: 3. Reserve Inventory
    InventorySvc-->>Orchestrator: OK
    Orchestrator-->>Client: Order Complete

    Note over Orchestrator: On failure: compensate in reverse
```'''),

    'circuit-breaker': ('Circuit Breaker', '''```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Failures exceed threshold
    Closed --> Closed: Success
    Open --> HalfOpen: Timeout expires
    Open --> Open: Reject requests
    HalfOpen --> Closed: Test succeeds
    HalfOpen --> Open: Test fails
```'''),

    'cdn': ('CDN Architecture', '''```mermaid
graph TB
    subgraph Users
        US[US Users]
        EU[EU Users]
    end
    subgraph Edge
        EdgeUS[Edge US]
        EdgeEU[Edge EU]
    end
    subgraph Origin
        LB[Load Balancer]
        Origin[Origin Server]
        S3[(Object Storage)]
    end
    US --> EdgeUS
    EU --> EdgeEU
    EdgeUS -->|miss| LB
    EdgeEU -->|miss| LB
    LB --> Origin
    Origin --> S3
```'''),
}


def list_diagrams():
    print("\n" + "=" * 50)
    print("AVAILABLE DIAGRAMS")
    print("=" * 50)
    for key, (name, _) in DIAGRAMS.items():
        print(f"  {key:18} - {name}")
    print()


def generate(diagram_type: str, output: str = None):
    if diagram_type not in DIAGRAMS:
        print(f"Error: Unknown type '{diagram_type}'. Use --list")
        sys.exit(1)

    name, template = DIAGRAMS[diagram_type]
    print(f"\n{'=' * 50}")
    print(name.upper())
    print("=" * 50)
    print(template)

    if output:
        with open(output, 'w') as f:
            f.write(f"# {name}\n\n{template}")
        print(f"\n✅ Saved to: {output}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Mermaid Diagram Generator')
    parser.add_argument('--list', '-l', action='store_true')
    parser.add_argument('--type', '-t', type=str)
    parser.add_argument('--output', '-o', type=str)
    parser.add_argument('--all', '-a', action='store_true')

    args = parser.parse_args()

    if args.list or len(sys.argv) == 1:
        list_diagrams()
    elif args.all:
        for dtype in DIAGRAMS:
            generate(dtype)
    elif args.type:
        generate(args.type, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
