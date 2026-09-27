// import "@supabase/functions-js/edge-runtime.d.ts";
// import { withSupabase } from "@supabase/server";
// import { createClient } from "@supabase/supabase-js";
import { UUID } from "node:crypto";

// const url = Deno.env.get("SUPABASE_URL") ?? "";
// const key = Deno.env.get("SUPABASE_KEY") ?? "";

// const supabase = createClient(
//   url,
//   key,
// );

type bytea = `\\x${string}`;

interface WebhookPayload {
  type: "INSERT";
  table: string;
  record: {
    originator_id: UUID;
    originator_version: number;
    topic: string;
    state: bytea;
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
