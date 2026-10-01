import os
from typing import Any, Callable

from eventsourcing.application import Application
from uuid import UUID

from eventsourcing.persistence import AggregateRecorder, ApplicationRecorder, InfrastructureFactory, JSONTranscoder
from eventsourcing.postgres import PostgresAggregateRecorder, PostgresApplicationRecorder, PostgresFactory
from eventsourcing.utils import Environment, resolve_topic
from psycopg.rows import DictRow
from psycopg import Connection


from app.domain import Payment, EntryMode, ThreeDSResult
from app.transcoders import CustomEnumTranscoding


class CustomPostgresFactory(PostgresFactory):

    events_table_name = os.getenv("EVENTS_TABLE_NAME") or "stored_events"

    def __init__(self, env: Environment):
        super().__init__(env)

        if hasattr(self, "datastore") and self.datastore:
            after_connect_func = self.datastore.after_connect_func

            def new_after_connect_func() -> Callable[[Connection[Any]], None]:
                after_connect = after_connect_func()

                def new_after_connect(conn: Connection[DictRow]) -> None:
                    after_connect(conn)
                    conn.prepare_threshold = 1

                return new_after_connect

            self.datastore.after_connect_func = new_after_connect_func

    def aggregate_recorder(self, purpose: str = "events") -> AggregateRecorder:

        recorder = PostgresAggregateRecorder(
            datastore=self.datastore, events_table_name=self.events_table_name)

        if self.env_create_table():
            recorder.create_table()

        return recorder

    def application_recorder(self) -> ApplicationRecorder:
        application_recorder_topic = self.env.get(
            self.APPLICATION_RECORDER_TOPIC)
        if application_recorder_topic:
            application_recorder_class: type[PostgresApplicationRecorder] = (
                resolve_topic(application_recorder_topic)
            )
            assert issubclass(application_recorder_class,
                              PostgresApplicationRecorder)
        else:
            application_recorder_class = type(self).application_recorder_class

        recorder = application_recorder_class(
            datastore=self.datastore,
            events_table_name=self.events_table_name,
        )

        self.datastore.enable_db_functions = True

        if self.env_create_table():
            recorder.create_table()
        return recorder


class PaymentApplication(Application[UUID]):

    def construct_factory(self, env: Environment) -> InfrastructureFactory:
        return CustomPostgresFactory(env)  # type: ignore

    def register_transcodings(self, transcoder: JSONTranscoder):
        super().register_transcodings(transcoder)

        enums_to_register: list[type] = [EntryMode, ThreeDSResult]

        for enum in enums_to_register:
            transcoder.register(CustomEnumTranscoding(enum))

    def request_payment(self, payment: Payment):
        payment.request()

        if not payment.validate():
            payment.decline()
        else:
            payment.approve()

        self.save(payment)
