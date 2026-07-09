import { describe, it, expect } from "vitest";
import apiClient from "./client";
import { http, HttpResponse } from "msw";
import { server } from "../test/mocks/server";

describe("API Client", () => {
  it("should unwrap successful envelope data", async () => {
    server.use(
      http.get("/api/v1/test", () => {
        return HttpResponse.json({
          success: true,
          data: { key: "value" },
          correlation_id: "123"
        });
      })
    );

    const data = await apiClient.get("/test");
    expect(data).toEqual({ key: "value", correlation_id: "123" });
  });

  it("should normalize error responses", async () => {
    server.use(
      http.get("/api/v1/error", () => {
        return HttpResponse.json({
          success: false,
          error_code: "VALIDATION_FAILED",
          message: "Invalid input"
        }, { status: 422 });
      })
    );

    try {
      await apiClient.get("/error");
    } catch (err: any) {
      expect(err.error_code).toBe("VALIDATION_FAILED");
      expect(err.message).toBe("Invalid input");
    }
  });
});
