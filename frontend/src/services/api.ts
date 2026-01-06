/**
 * API Client for Multi-Agent Chatbot Backend
 *
 * Handles all HTTP communication with the FastAPI server
 */

const API_BASE_URL = "http://localhost:8000/api";

// =============================================================================
// TYPE DEFINITIONS
// =============================================================================

export interface ChatRequest {
  session_id: string;
  message: string;
  agent: "personal" | "hr" | "it";
}

export interface Source {
  source: string;
  page: number;
  rank: number;
  preview: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  agent: "personal" | "hr" | "it";
  sources: Source[];
  needs_clarification: boolean;
  workflow_path: string[];
}

export interface SessionInfo {
  session_id: string;
  created_at: string;
  message_count: number;
  current_agent: string;
}

export interface HealthCheckResponse {
  status: "healthy" | "unhealthy";
  rag_initialized: boolean;
  graph_initialized: boolean;
}

export interface StreamEvent {
  type: "token" | "complete" | "error";
  content?: string;
  agent?: "personal" | "hr" | "it";
  sources?: Source[];
  workflow_path?: string[];
  error?: string;
}

// =============================================================================
// ERROR HANDLING
// =============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

// =============================================================================
// API CLIENT
// =============================================================================

export const chatAPI = {
  /**
   * Create a new chat session
   */
  async createSession(): Promise<SessionInfo> {
    try {
      const response = await fetch(`${API_BASE_URL}/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to create session" }));
        throw new APIError(
          error.detail || "Failed to create session",
          response.status,
          error
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(
        "Network error: Could not connect to server",
        undefined,
        error
      );
    }
  },

  /**
   * Get session information
   */
  async getSession(sessionId: string): Promise<SessionInfo> {
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Session not found" }));
        throw new APIError(
          error.detail || "Failed to get session",
          response.status,
          error
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(
        "Network error: Could not connect to server",
        undefined,
        error
      );
    }
  },

  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Failed to send message" }));
        throw new APIError(
          error.detail || "Failed to send message",
          response.status,
          error
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(
        "Network error: Could not connect to server",
        undefined,
        error
      );
    }
  },

  /**
   * Stream a chat message using Server-Sent Events (SSE)
   *
   * @param request - Chat request parameters
   * @param onToken - Callback fired for each token received
   * @param onComplete - Callback fired when streaming completes with metadata
   * @param onError - Callback fired on error
   * @returns Object with abort() method to cancel the stream
   */
  streamMessage(
    request: ChatRequest,
    onToken: (token: string) => void,
    onComplete: (data: { agent: string; sources: Source[]; workflow_path: string[] }) => void,
    onError: (error: string) => void
  ): { abort: () => void } {
    let aborted = false;
    const abortController = new AbortController();

    (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(request),
          signal: abortController.signal,
        });

        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Failed to stream message" }));
          throw new APIError(
            error.detail || "Failed to stream message",
            response.status,
            error
          );
        }

        if (!response.body) {
          throw new APIError("No response body received");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (!aborted) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");

          // Keep the last incomplete chunk in buffer
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (aborted) break;
            if (!line.trim()) continue;

            // Parse SSE format: "event: <type>\ndata: <json>"
            const eventMatch = line.match(/^event:\s*(\w+)\ndata:\s*(.+)$/s);
            if (!eventMatch) continue;

            const [, eventType, eventData] = eventMatch;

            try {
              const data = JSON.parse(eventData);

              if (eventType === "token") {
                if (data.content) {
                  onToken(data.content);
                }
              } else if (eventType === "complete") {
                onComplete({
                  agent: data.agent || request.agent,
                  sources: data.sources || [],
                  workflow_path: data.workflow_path || [],
                });
              } else if (eventType === "error") {
                onError(data.error || "Unknown streaming error");
              }
            } catch (parseError) {
              console.error("Failed to parse SSE event data:", parseError);
            }
          }
        }
      } catch (error) {
        if (aborted) return; // Don't report errors after abort

        if (error instanceof APIError) {
          onError(error.message);
        } else if (error instanceof Error) {
          onError(error.name === "AbortError" ? "Stream cancelled" : error.message);
        } else {
          onError("Network error: Could not connect to server");
        }
      }
    })();

    return {
      abort: () => {
        aborted = true;
        abortController.abort();
      },
    };
  },

  /**
   * Check server health status
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new APIError("Health check failed", response.status);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(
        "Network error: Could not connect to server",
        undefined,
        error
      );
    }
  },
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Check if server is available
 */
export async function isServerAvailable(): Promise<boolean> {
  try {
    const health = await chatAPI.healthCheck();
    return health.status === "healthy";
  } catch {
    return false;
  }
}

/**
 * Wait for server to become available (useful for development)
 */
export async function waitForServer(
  maxAttempts: number = 10,
  delayMs: number = 1000
): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    if (await isServerAvailable()) {
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, delayMs));
  }
  return false;
}
