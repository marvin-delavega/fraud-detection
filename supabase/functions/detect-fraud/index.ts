import { UUID } from "node:crypto";

interface WebhookPayload {
  type: "INSERT";
  table: string;
  record: {
    originator_id: UUID;
    originator_version: number;
    topic: string;
    state: string;
    notification_id: number;
  };
  schema: string;
}

Deno.serve(async (req) => {
  try {
    const payload: WebhookPayload = await req.json();

    if (payload.table !== "events" || payload.type !== "INSERT") {
      return new Response("Event not handled", { status: 200 });
    }

    return new Response("Event handled", { status: 200 });
  } catch (err) {
    console.error("Webhook error:", err);
    return new Response("Server error", { status: 500 });
  }
});
