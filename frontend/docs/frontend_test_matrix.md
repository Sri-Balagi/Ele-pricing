# Frontend Test Matrix

The frontend testing strategy focuses on validating the integration between the UI components and the Backend API contract. Since there is zero business logic, unit tests focus heavily on data extraction and normalization.

## Core Tooling
- **Vitest**: The primary test runner (compatible with Vite).
- **React Testing Library (RTL)**: For rendering components and asserting DOM state.
- **Mock Service Worker (MSW)**: For intercepting HTTP requests at the network level.

## Mock Scenarios (MSW Handlers)
Located in `src/test/mocks/handlers.ts`, MSW intercepts requests matching `/api/v1/*` and returns controlled JSON responses.
1. **Success Scenarios**: Returns `200 OK` or `201 Created` with standard `APISuccessEnvelope` format.
2. **Validation Failure (422)**: Simulates the backend returning an `HTTPValidationError` payload, ensuring the `client.ts` interceptor normalizes it correctly.
3. **Network Failure / 500**: Used in edge-case tests to verify the global `ErrorBoundary` and TanStack Query error states trigger correctly.

## Coverage Focus
- **API Client Interceptor (`client.test.ts`)**: Tests ensure that `x-correlation-id` headers are correctly extracted and attached to the payload, and that standard success envelopes are cleanly unwrapped so components don't have to deal with nested `.data.data` access.
- **UI Store**: Ensures toggling themes modifies the internal state correctly.

## Future Integration / E2E
Currently, the testing suite focuses on component and API client boundaries. 
For Milestone 8/Production, **Playwright** is recommended to execute full Browser End-to-End tests simulating a real user workflow:
1. Load `/wizard`.
2. Enter Configuration Data.
3. Assert API `POST` is triggered.
4. Navigate to `/pricing`.
5. Assert Pricing UI renders correctly based on the mock backend response.
