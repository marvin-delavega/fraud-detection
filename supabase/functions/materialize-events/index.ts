import "@supabase/functions-js/edge-runtime.d.ts";
import { withSupabase } from "@supabase/server";
import { createClient } from "@supabase/supabase-js";
import { UUID } from "node:crypto";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL") ?? "",
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
);

const queue_name = "events";
const batch_size = 10;
const wait_in_seconds = 0;

interface QueueMessage {
  msg_id: bigint;
  read_ct: number;
  vt: string;
  enqueued_at: string;
  message: any;
}

interface Event {
  originator_id: UUID;
  originator_version: number;
  topic: string;
  state: string;
  notification_id: number;
}

export default {
  fetch: withSupabase({ auth: ["publishable", "secret"] }, async (req, ctx) => {
    console.log(
      `Consuming messages from ${queue_name} queue in batches of ${batch_size} with ${wait_in_seconds} sec wait time`,
    );

    const { data: messages, error } = await supabase.schema("pgmq_public").rpc(
      "read",
      {
        queue_name: queue_name,
        sleep_seconds: wait_in_seconds,
        n: batch_size,
      },
    );

    if (error) {
      console.log(`Error reading from ${queue_name} queue: `, error);
      return Response.json(JSON.stringify({ message: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (messages.length === 0) {
      console.log(`No messages found in ${queue_name} queue`);
      return Response.json(JSON.stringify({ message: "No messages found" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    console.log(
      `Received ${messages.length} messages from ${queue_name} queue`,
    );

    for (const message of messages) {
      const msg = message as QueueMessage;

      // Here you can add your logic to process the event

      const { error } = await supabase.schema("pgmq_public").rpc("archive", {
        queue_name: queue_name,
        message_id: message.msg_id,
      });

      if (error) {
        console.log(`Error archiving message #${message.msg_id}`, error);
        return Response.json(JSON.stringify({ message: error.message }), {
          status: 500,
          headers: { "Content-Type": "application/json" },
        });
      }

      console.log(`Archived message #${message.msg_id}`);
    }

    return Response.json(
      JSON.stringify({ message: `Materialized ${messages.length} messages` }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      },
    );
  }),
};
