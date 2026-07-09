# Master Architecture Diagram

This diagram visually summarizes the entire Elevator Configurator platform, illustrating the complete lifecycle of a request from the React UI down through the frozen Backend Architecture and back.

```mermaid
flowchart TD
    %% Frontend Layer
    subgraph Frontend ["Frontend Application (React 19)"]
        UI["React UI Components\n(Pages, Forms, DataTables)"]
        Zustand["Zustand\n(Local UI State)"]
        RQ["TanStack Query\n(Server State Cache)"]
        Axios["Axios Client\n(Interceptor & Envelope Unwrap)"]
        
        UI <--> Zustand
        UI <--> RQ
        RQ <--> Axios
    end

    %% Network Layer
    subgraph Network ["Network Boundary"]
        HTTP["HTTP REST API (JSON)\nx-correlation-id attached"]
    end

    Axios <--> HTTP

    %% Backend Layer
    subgraph Backend ["Backend Version 1.0.0 (Frozen Architecture)"]
        FastAPI["FastAPI App\n(API Router & Endpoint Handlers)"]
        
        subgraph Pipeline ["Configuration Pipeline"]
            direction TB
            RE["1. Rule Engine\n(Validation & Conflicts)"]
            DE["2. Dependency Engine\n(Resolution & Exclusions)"]
            BOMGen["3. BOM Generator\n(Part Extractor)"]
            PE["4. Pricing Engine\n(Tax & Discounts)"]
            QG["5. Quote Generator\n(Metadata Injection)"]
            
            RE --> DE
            DE --> BOMGen
            BOMGen --> PE
            PE --> QG
        end
        
        subgraph Storage ["Repository Layer"]
            DB[(PostgreSQL / SQLite\nConfiguration Storage)]
            Catalog[(Static Parts Catalog)]
        end

        subgraph Exporters ["Export Framework"]
            JSON["JSON Exporter"]
            PDF["PDF Exporter"]
            EXCEL["Excel Exporter"]
        end
        
        FastAPI <--> Pipeline
        Pipeline <--> Storage
        FastAPI --> Exporters
    end

    HTTP <--> FastAPI
```

## Flow Description
1. The **React UI** triggers an action (e.g., submitting the Configuration Wizard).
2. The mutation is passed to **TanStack Query**, which invokes the **Axios Client**.
3. The Axios Client issues an **HTTP REST** call across the network boundary to the **FastAPI** backend.
4. FastAPI passes the DTO into the **Configuration Pipeline**.
5. The Pipeline executes sequentially:
   - **Rule Engine** asserts hard constraints.
   - **Dependency Engine** resolves feature prerequisites.
   - **BOM Generator** extracts physical parts.
   - **Pricing Engine** calculates final costs.
   - **Quote Generator** wraps the payload in metadata.
6. The updated configuration is stored in the **Repository Layer**.
7. FastAPI returns an `APISuccessEnvelope` to the Frontend.
8. Axios intercepts the envelope, strips it to the pure data payload, and updates **TanStack Query**.
9. The **React UI** automatically re-renders with the fresh data (BOM, Pricing, Validation).
10. If the user clicks "Export", FastAPI directs the final payload to the **Export Framework**, streaming the resulting file back to the browser.
