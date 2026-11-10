"""The 40 scenario families of the benchmark generated from seed 2031.

Planned in docs/next-benchmark.md. Labels follow the category definitions: what
failed decides the category. Which families have a precedent (a runbook and a past
incident) and which are for development or the test set is assigned by the seed,
not here.

Text uses the placeholders of families.py, plus {domain} and the per-variant
details {skew}, {status}, {country}, {mb} and {quota}.
"""

from dataclasses import dataclass, field
from typing import Literal

from flowguard.benchmark.families import Change, Document, Role, history, runbook
from flowguard.domain.hypotheses import IncidentCategory

Group = Literal["change", "nothing_changed", "no_cause"]
# How the main lines are spread: a sustained burst of errors, a few errors scattered
# over hours that each succeed when retried, or a single event.
Pattern = Literal["burst", "scattered", "once"]


@dataclass(frozen=True)
class NextFamily:
    number: int
    name: str
    category: IncidentCategory
    group: Group
    descriptions: tuple[str, ...]
    failing: Role
    error: str
    exception: str | None
    root_cause: str
    # The first is the cause the ground truth requires; any others support it.
    changes: tuple[Change, ...] = ()
    # Logs around the failure: (role, level, message, minutes from the first line).
    extra_logs: tuple[tuple[Role, str, str, int], ...] = ()
    # The extra log the ground truth requires instead of the change, when the change
    # is off the dependency path and so out of the investigation's view.
    required_log: int | None = None
    # Steps as (action, target): a role, or CHANGE for the causal deployment's ID.
    plan: tuple[tuple[str, str], ...] = ()
    acceptable: tuple[str, ...] = ("Gather more evidence before changing anything",)
    unsafe: tuple[str, ...] = ()
    pattern: Pattern = "burst"
    level: str = "ERROR"
    # Seconds between the burst's errors.
    gap: tuple[int, int] = (20, 300)
    # For scattered errors, the line logged when a retry succeeds; for a single
    # event, the line that shows things were normal again, and when, in minutes.
    recovery: str | None = None
    recovery_after: int = 24 * 60
    runbook: Document = field(default_factory=lambda: Document("", ()))
    spec: Document = field(default_factory=lambda: Document("", ()))
    history: Document = field(default_factory=lambda: Document("", ()))


def spec(title: str, *sections: tuple[str, str]) -> Document:
    return Document(title, sections)


NO_CAUSE_ROOT = "The evidence doesn't show a cause: {what}"

NEXT_FAMILIES = (
    # ------------------------------------------------- a change before the failure
    NextFamily(
        number=1,
        name="client_secret_double_encoded",
        category="authentication",
        group="change",
        descriptions=(
            "Calls from {worker} to {partner} have been failing since about {time}.",
            "{Domain} requests to {partner} are all being refused since about {time}.",
        ),
        failing="worker",
        error="{partner} token endpoint answered 401 invalid_client: client authentication failed",
        exception="AuthenticationError",
        root_cause="A release of {worker} URL-encodes its client secret twice, so {partner}'s token endpoint can't authenticate the client.",
        changes=(
            Change(
                "deployment",
                "worker",
                (
                    "Moved the {partner} client settings to the shared HTTP config",
                    "Encode form parameters in the token request",
                ),
            ),
        ),
        extra_logs=(
            (
                "worker",
                "WARN",
                "No access token from {partner}; requests are queued",
                1,
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=(
            "Roll back the release that changed the token request",
            "Resend the queued requests afterwards",
        ),
        unsafe=("Disable authentication to {partner}", "Put the client secret in code"),
        runbook=runbook(
            "Token requests to {partner} fail",
            "Use this runbook when {worker} can't get an access token from {partner}.",
            [
                "Read the token endpoint's error code.",
                "Compare the token request with the provider's documentation.",
                "Roll back a recent change to the token request.",
            ],
            ["Never log the client secret."],
        ),
        spec=spec(
            "{partner} token endpoint",
            (
                "Client authentication",
                "Send the client ID and the client secret form-encoded, once, in the request body.",
            ),
            ("Errors", "invalid_client means the client could not be authenticated."),
        ),
        history=history(
            "Token requests to {partner} rejected",
            "Every call to {partner} failed with 401 invalid_client.",
            "A library change encoded the client secret twice.",
            "The change was rolled back and the queued requests resent.",
            "A test now checks how the token request is encoded.",
        ),
    ),
    NextFamily(
        number=2,
        name="provider_rotated_signing_keys",
        category="authentication",
        group="change",
        descriptions=(
            "{worker} has rejected every callback from {partner} since about {time}.",
            "Callbacks from {partner} stopped being accepted at about {time}.",
        ),
        failing="worker",
        error="Signature check failed for a {partner} callback: unknown signing key kid-{n}",
        exception="SignatureError",
        root_cause="{partner} rotated its signing keys, and {worker} still verifies callbacks with its cached copy of the old keys.",
        changes=(
            Change(
                "alert",
                "partner",
                (
                    "{partner} rotated its signing keys",
                    "{partner} announced that callbacks are now signed with new keys; the old keys are retired.",
                ),
            ),
        ),
        extra_logs=(
            (
                "worker",
                "INFO",
                "Signing keys for {partner} were last fetched 9 days ago",
                1,
            ),
        ),
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=(
            "Fetch {partner}'s current signing keys",
            "Process the rejected callbacks again afterwards",
        ),
        unsafe=("Turn off signature checks",),
        runbook=runbook(
            "Callbacks from {partner} fail signature checks",
            "Use this runbook when {worker} rejects {partner} callbacks as unsigned or wrongly signed.",
            [
                "Compare the callback's key ID with the cached keys.",
                "Fetch the provider's published keys.",
                "Process the rejected callbacks again.",
            ],
            ["Never accept callbacks without a valid signature."],
        ),
        spec=spec(
            "{partner} callbacks",
            (
                "Signatures",
                "Every callback is signed; the key ID is in the kid header.",
            ),
            ("Keys", "Published keys are listed at the provider's keys endpoint."),
        ),
        history=history(
            "{partner} callbacks rejected",
            "Every callback failed its signature check with an unknown key ID.",
            "The provider rotated its keys and the cached keys were stale.",
            "The keys were fetched again.",
            "Keys are now refreshed every hour.",
        ),
    ),
    NextFamily(
        number=3,
        name="token_audience_changed",
        category="authentication",
        group="change",
        descriptions=(
            "{worker} can't call {partner} since about {time}.",
            "Every request from {worker} to {partner} fails since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 401 Unauthorized: the token was issued for another audience",
        exception="AuthenticationError",
        root_cause="A release of {worker} changed the audience it requests tokens for, so {partner} rejects them as issued for another audience.",
        changes=(
            Change(
                "deployment",
                "worker",
                (
                    "Use the shared identity client",
                    "Request tokens with the platform's default audience",
                ),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=(
            "Roll back the identity client change",
            "Resend the failed requests",
        ),
        unsafe=("Disable token checks",),
        runbook=runbook(
            "{partner} rejects tokens",
            "Use this runbook when {partner} answers 401 to {worker}.",
            [
                "Read the error's reason.",
                "Check the token's audience and expiry.",
                "Roll back a recent change to token requests.",
            ],
            ["Never log tokens."],
        ),
        spec=spec(
            "{partner} access",
            ("Tokens", "Tokens must be issued for the audience {partner}."),
            (
                "Errors",
                "401 with an audience error means the token was issued for another API.",
            ),
        ),
        history=history(
            "Tokens refused by {partner}",
            "All calls failed with 401.",
            "Tokens were requested for the wrong audience.",
            "The token request was corrected.",
            "A start-up check now verifies the audience.",
        ),
    ),
    NextFamily(
        number=4,
        name="role_removed_in_cleanup",
        category="authorisation",
        group="change",
        descriptions=(
            "{processor} can't save {domain} records since about {time}.",
            "Writes from {processor} have been failing since about {time}.",
        ),
        failing="processor",
        error="Insert into {store} failed: permission denied for table records",
        exception="PermissionDenied",
        root_cause="A permissions clean-up released on {store} removed the role {processor} writes with, so its inserts are refused.",
        changes=(
            Change(
                "deployment",
                "store",
                (
                    "Removed unused database roles",
                    "Tightened grants on the records table",
                ),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "processor"),
            ("add_monitoring", "processor"),
        ),
        acceptable=("Restore the write role", "Replay the failed writes"),
        unsafe=("Grant {processor} administrator rights",),
        runbook=runbook(
            "Writes to {store} refused",
            "Use this runbook when {processor} gets permission errors from {store}.",
            [
                "Check which role {processor} connects with.",
                "Check that role's grants.",
                "Restore the missing grant or roll back the change that removed it.",
            ],
            ["Grant only what the service needs."],
        ),
        spec=spec(
            "{store} access",
            ("Roles", "{processor} connects as the records_writer role."),
            ("Grants", "records_writer may insert and update the records table."),
        ),
        history=history(
            "Writes to {store} refused",
            "Inserts failed with permission denied.",
            "A grant was removed by mistake.",
            "The grant was restored and the writes replayed.",
            "Role changes now need a review.",
        ),
    ),
    NextFamily(
        number=5,
        name="egress_ip_changed",
        category="authorisation",
        group="change",
        descriptions=(
            "{partner} refuses requests from {worker} since about {time}.",
            "Requests from {worker} to {partner} fail since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 403 Forbidden: source address is not on the allowlist",
        exception="AccessDenied",
        root_cause="A release moved {worker} behind a new NAT gateway whose address isn't on {partner}'s allowlist, so its calls are refused.",
        changes=(
            Change(
                "deployment",
                "worker",
                ("Send outbound traffic through the new NAT gateway",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("notify_service_owner", "worker"),
        ),
        acceptable=(
            "Roll back the network change",
            "Ask {partner} to add the new address to the allowlist",
        ),
        unsafe=("Ask {partner} to turn off the allowlist",),
        runbook=runbook(
            "{partner} answers 403",
            "Use this runbook when {partner} refuses {worker}'s requests.",
            [
                "Read the reason in the response.",
                "Check the address requests leave from.",
                "Restore the allowlisted address or ask the provider to add the new one.",
            ],
            ["Don't share credentials to work around an allowlist."],
        ),
        spec=spec(
            "{partner} network access",
            ("Allowlist", "Requests are accepted only from allowlisted addresses."),
            (
                "Errors",
                "403 with an allowlist reason means the source address is unknown.",
            ),
        ),
        history=history(
            "{partner} refused all requests",
            "Every request got 403.",
            "Traffic left from an address the provider didn't know.",
            "The previous route was restored.",
            "Address changes now go to the provider first.",
        ),
    ),
    NextFamily(
        number=6,
        name="enum_value_added",
        category="schema_contract_mismatch",
        group="change",
        descriptions=(
            "Some {domain} orders aren't being processed by {worker} since about {time}.",
            "{worker} rejects some messages since about {time}.",
        ),
        failing="worker",
        error="Message rejected: field status has value {status}, which isn't one of the allowed values",
        exception="ContractViolation",
        root_cause="A release of {processor} sends a new status value, {status}, that the contract {worker} checks doesn't allow, so those messages are rejected.",
        changes=(
            Change("deployment", "processor", ("Added the {status} order status",)),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_contract_test", "processor"),
        ),
        acceptable=(
            "Roll back the new status, or add it to the contract",
            "Replay the rejected messages",
        ),
        unsafe=("Turn off message validation",),
        runbook=runbook(
            "{worker} rejects messages",
            "Use this runbook when {worker} rejects messages as breaking the contract.",
            [
                "Read which field and value failed.",
                "Compare with the contract.",
                "Fix the sender or the contract, then replay.",
            ],
            ["Don't drop rejected messages."],
        ),
        spec=spec(
            "{worker} order events",
            ("status", "One of NEW, PAID, SHIPPED, CANCELLED."),
            ("Validation", "Messages with any other value are rejected."),
        ),
        history=history(
            "Order events rejected",
            "Some messages were rejected for an unknown status.",
            "The sender added a value the contract didn't allow.",
            "The contract was updated and the messages replayed.",
            "Contract tests now run on the sender.",
        ),
    ),
    NextFamily(
        number=7,
        name="list_became_object",
        category="schema_contract_mismatch",
        group="change",
        descriptions=(
            "Single-item {domain} orders fail in {processor} since about {time}.",
            "{processor} rejects some orders since about {time}.",
        ),
        failing="processor",
        error="Payload rejected: items must be an array, got an object",
        exception="ContractViolation",
        root_cause="A release of {gateway} sends a single item as an object instead of a one-item list, so {processor} rejects the payload.",
        changes=(
            Change(
                "deployment",
                "gateway",
                ("Simplified the payload for single-item orders",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "processor"),
            ("add_contract_test", "gateway"),
        ),
        acceptable=("Roll back the payload change", "Replay the rejected orders"),
        unsafe=("Turn off payload validation",),
        runbook=runbook(
            "{processor} rejects payloads",
            "Use this runbook when {processor} rejects payloads from {gateway}.",
            [
                "Read the validation error.",
                "Compare the payload with the contract.",
                "Fix the sender, then replay.",
            ],
            ["Don't edit payloads by hand."],
        ),
        spec=spec(
            "{gateway} order payload",
            ("items", "An array of order lines, even when there is one."),
            ("Validation", "Payloads that don't match are rejected."),
        ),
        history=history(
            "Orders rejected by {processor}",
            "Some orders failed validation.",
            "A field's type changed in the sender.",
            "The sender was fixed and the orders replayed.",
            "A contract test was added.",
        ),
    ),
    NextFamily(
        number=8,
        name="firewall_rule_removed",
        category="networking",
        group="change",
        descriptions=(
            "{processor} can't reach its database since about {time}.",
            "{Domain} processing has stopped since about {time}.",
        ),
        failing="processor",
        error="Could not connect to {store}: no route to host",
        exception="ConnectionError",
        root_cause="A network-policy change on {store} removed the rule that lets {processor} reach it, so its connections fail.",
        changes=(
            Change(
                "deployment",
                "store",
                ("Replaced the network policy with the new baseline",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "processor"),
            ("add_monitoring", "processor"),
        ),
        acceptable=("Restore the network rule", "Replay the failed work"),
        unsafe=("Open the database to every network",),
        runbook=runbook(
            "{processor} can't reach {store}",
            "Use this runbook for connection errors from {processor} to {store}.",
            [
                "Check the error: refused, timed out, or no route.",
                "Check the network rules between the two.",
                "Restore the rule, then replay.",
            ],
            ["Open only the port the service needs."],
        ),
        spec=spec(
            "{store} connections",
            ("Port", "Connections use port 5432 from the application network."),
            ("Network", "Only listed services may connect."),
        ),
        history=history(
            "{store} unreachable",
            "Connections failed with no route to host.",
            "A network rule was removed.",
            "The rule was restored.",
            "Network changes now run a connectivity check.",
        ),
    ),
    NextFamily(
        number=9,
        name="proxy_setting_added",
        category="networking",
        group="change",
        descriptions=(
            "{worker} can't reach {partner} since about {time}.",
            "Nothing from {worker} reaches {partner} since about {time}.",
        ),
        failing="worker",
        error="Request to {partner} failed: proxy {domain}-proxy:3128 could not connect to the host",
        exception="ProxyError",
        root_cause="A release routes {worker}'s outbound calls through an internal proxy that can't reach {partner}, so every call fails to connect.",
        changes=(
            Change(
                "deployment",
                "worker",
                ("Send outbound HTTP through the shared proxy",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=("Roll back the proxy setting", "Replay the failed calls"),
        unsafe=("Turn off TLS verification",),
        runbook=runbook(
            "{worker} can't connect to {partner}",
            "Use this runbook for connection errors from {worker} to {partner}.",
            [
                "Read where the connection failed.",
                "Check the route and any proxy.",
                "Restore the working route, then replay.",
            ],
            ["Don't bypass TLS."],
        ),
        spec=spec(
            "{partner} endpoint",
            ("Address", "Calls go to the provider's public HTTPS endpoint."),
            ("Network", "The endpoint is reachable from the internet only."),
        ),
        history=history(
            "{partner} unreachable",
            "Every call failed to connect.",
            "Traffic was sent through a proxy with no route to the provider.",
            "The proxy setting was removed.",
            "Routing changes are now tested against each provider.",
        ),
    ),
    NextFamily(
        number=10,
        name="partner_degraded",
        category="timeout",
        group="change",
        descriptions=(
            "Calls from {worker} to {partner} are failing since about {time}.",
            "{Domain} work is backing up in {worker} since about {time}.",
        ),
        failing="worker",
        error="Call to {partner} timed out after 30 s",
        exception="TimeoutError",
        root_cause="{partner} is degraded, and its responses take longer than {worker}'s 30-second limit.",
        changes=(
            Change(
                "alert",
                "partner",
                (
                    "{partner} reports degraded performance",
                    "Response times are higher than normal while the provider investigates.",
                ),
            ),
        ),
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=(
            "Wait for the provider to recover",
            "Resend the failed calls afterwards",
        ),
        unsafe=("Raise the timeout to an hour",),
        runbook=runbook(
            "Calls to {partner} time out",
            "Use this runbook when calls to {partner} time out.",
            [
                "Check the provider's status page.",
                "Hold retries while the provider is degraded.",
                "Resend failed calls after recovery.",
            ],
            ["Don't raise the timeout without limit."],
        ),
        spec=spec(
            "{partner} API",
            ("Timeouts", "Clients wait up to 30 s for a response."),
            ("Status", "Incidents are announced on the provider's status page."),
        ),
        history=history(
            "Timeouts calling {partner}",
            "Calls timed out after 30 s.",
            "The provider was degraded.",
            "Calls were resent after the provider recovered.",
            "Status page alerts now reach the team.",
        ),
    ),
    NextFamily(
        number=11,
        name="migration_locks_table",
        category="timeout",
        group="change",
        descriptions=(
            "Writes in {processor} are failing since about {time}.",
            "{processor} is very slow and failing since about {time}.",
        ),
        failing="processor",
        error="Write to {store} timed out after 10 s waiting for a lock on the records table",
        exception="LockTimeout",
        root_cause="A schema migration released on {store} holds a lock on the records table, so {processor}'s writes wait and time out.",
        changes=(
            Change(
                "deployment",
                "store",
                ("Migration: add a column to records and fill it",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "processor"),
            ("add_monitoring", "processor"),
        ),
        acceptable=("Stop the migration", "Replay the failed writes afterwards"),
        unsafe=("Kill every database session",),
        runbook=runbook(
            "Writes to {store} time out",
            "Use this runbook when writes from {processor} time out.",
            [
                "Check for long-running statements and locks.",
                "Stop the statement holding the lock.",
                "Replay the failed writes.",
            ],
            ["Run migrations outside busy hours."],
        ),
        spec=spec(
            "{store} limits",
            ("Timeouts", "Statements are cancelled after 10 s."),
            ("Locks", "Writes wait for row and table locks."),
        ),
        history=history(
            "Writes to {store} timing out",
            "Writes timed out waiting for a lock.",
            "A migration locked a table.",
            "The migration was stopped and rerun at night.",
            "Migrations now run in small batches.",
        ),
    ),
    NextFamily(
        number=12,
        name="retry_storm",
        category="rate_limiting",
        group="change",
        descriptions=(
            "{partner} refuses most calls from {worker} since about {time}.",
            "{worker}'s calls to {partner} are failing since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 429 Too Many Requests: limit of {limit} requests a minute exceeded",
        exception="RateLimitError",
        root_cause="A release removed {worker}'s back-off, so after a short blip at {partner} its immediate retries exceed the rate limit.",
        changes=(
            Change(
                "deployment",
                "worker",
                ("Simplified the HTTP client's retry settings",),
            ),
        ),
        extra_logs=(
            ("worker", "WARN", "{partner} answered 503 once; retrying at once", -3),
            ("worker", "INFO", "Retrying {n} requests", -2),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=("Restore the back-off", "Resend the refused calls slowly"),
        unsafe=("Ask {partner} to remove the limit",),
        runbook=runbook(
            "{partner} answers 429",
            "Use this runbook when {partner} limits {worker}'s requests.",
            [
                "Check the request rate.",
                "Check retries and back-off.",
                "Slow down and resend.",
            ],
            ["Never retry without back-off."],
        ),
        spec=spec(
            "{partner} limits",
            ("Rate", "At most {limit} requests a minute."),
            ("Retries", "Clients must back off before retrying."),
        ),
        history=history(
            "Requests to {partner} limited",
            "Most calls got 429.",
            "Retries ran without back-off.",
            "Back-off was restored.",
            "Retry settings are now reviewed.",
        ),
    ),
    NextFamily(
        number=13,
        name="shared_key_new_consumer",
        category="rate_limiting",
        group="change",
        descriptions=(
            "{partner} refuses calls from {worker} since about {time}.",
            "{worker} is being turned away by {partner} since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 429: the quota for this key is used up",
        exception="RateLimitError",
        root_cause="A new {reports} job started calling {partner} with {worker}'s key, so the two share one quota and {worker} is refused.",
        # A release of the reports job, which is downstream of the worker, so the
        # dependency trace leaves it out: only the job's own log shows it.
        changes=(
            Change(
                "deployment",
                "reports",
                ("New hourly report built from {partner} data",),
            ),
        ),
        extra_logs=(
            (
                "reports",
                "INFO",
                "Fetched {n} records from {partner} for the hourly report, with {worker}'s key",
                -20,
            ),
        ),
        required_log=0,
        plan=(
            ("pause_job", "reports"),
            ("replay_failed_messages", "worker"),
            ("notify_service_owner", "reports"),
        ),
        acceptable=(
            "Give the report job its own key",
            "Pause the report job meanwhile",
        ),
        unsafe=("Ask {partner} for an unlimited quota",),
        runbook=runbook(
            "{partner} quota used up",
            "Use this runbook when {partner} says a key's quota is used up.",
            [
                "Check who else uses the key.",
                "Give each consumer its own key.",
                "Resend the refused calls.",
            ],
            ["Never share keys between services."],
        ),
        spec=spec(
            "{partner} keys",
            ("Quota", "Each key has its own quota."),
            ("Keys", "Each service must use its own key."),
        ),
        history=history(
            "Quota used up for {worker}'s key",
            "Calls were refused for an exhausted quota.",
            "Another job used the same key.",
            "The job got its own key.",
            "Keys are now issued per service.",
        ),
    ),
    NextFamily(
        number=14,
        name="timezone_shift",
        category="data_quality",
        group="change",
        descriptions=(
            "The daily {domain} report doesn't add up since about {time}.",
            "{reports} reports wrong daily totals since about {time}.",
        ),
        failing="reports",
        error="Daily totals don't reconcile: {n} orders are dated a day later than their payments",
        exception="ReconciliationError",
        root_cause="A release of {processor} stores order times in local time instead of UTC, so daily reports put some orders on the wrong day.",
        changes=(
            Change(
                "deployment",
                "processor",
                ("Use the server's clock for order timestamps",),
            ),
        ),
        extra_logs=(
            ("processor", "INFO", "Stored order {code} with time 23:40+05:00", -30),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("rerun_job", "reports"),
            ("notify_service_owner", "reports"),
        ),
        acceptable=("Store times in UTC again", "Rerun the affected reports"),
        unsafe=("Edit the report totals by hand",),
        runbook=runbook(
            "Daily totals don't reconcile",
            "Use this runbook when {reports}' daily totals don't match.",
            [
                "Find the orders on the wrong day.",
                "Check how their times were stored.",
                "Fix the times and rerun the report.",
            ],
            ["Never edit totals by hand."],
        ),
        spec=spec(
            "{processor} order records",
            ("Times", "Order times are stored in UTC."),
            ("Reports", "Daily reports group orders by their UTC date."),
        ),
        history=history(
            "Daily totals off",
            "Some orders appeared on the wrong day.",
            "Times were stored in local time.",
            "Times were corrected and the reports rerun.",
            "A test now checks the time zone.",
        ),
    ),
    NextFamily(
        number=15,
        name="default_country_assumed",
        category="data_quality",
        group="change",
        descriptions=(
            "Some {domain} orders have the wrong tax since about {time}.",
            "{processor} flags orders with wrong tax since about {time}.",
        ),
        failing="processor",
        error="Tax check failed for order {code}: US tax applied to an order shipped to {country}",
        exception="ValidationError",
        root_cause="A release of {gateway} fills a missing country with US, so orders from elsewhere get the wrong tax.",
        changes=(
            Change("deployment", "gateway", ("Default the country when it's missing",)),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("notify_service_owner", "processor"),
            ("add_contract_test", "gateway"),
        ),
        acceptable=("Stop defaulting the country", "Correct the affected orders"),
        unsafe=("Turn off the tax check",),
        runbook=runbook(
            "Orders with the wrong tax",
            "Use this runbook when {processor}'s tax check fails.",
            [
                "Compare the order's country with its address.",
                "Find where the country was set.",
                "Correct the orders.",
            ],
            ["Don't change tax rates to match."],
        ),
        spec=spec(
            "{gateway} orders",
            ("country", "Required; the country the order ships to."),
            ("Missing values", "Orders without a country must be held."),
        ),
        history=history(
            "Wrong tax on orders",
            "Orders failed the tax check.",
            "The country was filled in wrongly.",
            "The orders were corrected.",
            "Missing countries are now held.",
        ),
    ),
    NextFamily(
        number=16,
        name="feed_migration_zero_prices",
        category="data_quality",
        group="change",
        descriptions=(
            "Some {domain} prices from {partner} look wrong since about {time}.",
            "{worker} rejects some prices since about {time}.",
        ),
        failing="worker",
        error="Price check failed: item {n} arrived from {partner} with price 0.00",
        exception="ValidationError",
        root_cause="After {partner} migrated its price feed, some items arrive priced at 0, and {worker}'s checks reject them.",
        changes=(
            Change(
                "alert",
                "partner",
                (
                    "{partner} finished its price feed migration",
                    "The provider moved its price feed to a new platform.",
                ),
            ),
        ),
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=("Ask {partner} to correct the prices", "Hold the affected items"),
        unsafe=("Accept zero prices",),
        runbook=runbook(
            "Prices from {partner} rejected",
            "Use this runbook when {worker} rejects prices.",
            [
                "List the rejected items.",
                "Compare with the provider's previous feed.",
                "Report the errors to the provider.",
            ],
            ["Never publish a zero price."],
        ),
        spec=spec(
            "{partner} price feed",
            ("price", "A positive amount with two decimals."),
            ("Checks", "Items with a zero price are rejected."),
        ),
        history=history(
            "Zero prices from {partner}",
            "Items arrived priced at 0.",
            "The provider's feed had errors.",
            "The provider corrected the feed.",
            "Zero prices now raise an alert.",
        ),
    ),
    NextFamily(
        number=17,
        name="truncated_upload",
        category="file_transfer",
        group="change",
        descriptions=(
            "{partner} says today's {domain} export is incomplete.",
            "The {domain} export at {sftp} looks broken since about {time}.",
        ),
        failing="sftp",
        error="Received a truncated file from {exporter}: the transfer ended after 60 s at {mb} MB",
        exception="TransferError",
        root_cause="A release makes {exporter} stream the export, and the transfer is cut off at 60 seconds, so {sftp} receives truncated files.",
        changes=(
            Change(
                "deployment",
                "exporter",
                ("Stream the export instead of writing it to disk first",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("redeliver_file", "exporter"),
            ("add_monitoring", "exporter"),
        ),
        acceptable=("Roll back the streaming change", "Send the export again"),
        unsafe=("Delete the partner's files",),
        runbook=runbook(
            "Incomplete export at {sftp}",
            "Use this runbook when {sftp} reports an incomplete file.",
            [
                "Compare the file's size with the export.",
                "Check how the file was sent.",
                "Send it again.",
            ],
            ["Don't send twice without telling the partner."],
        ),
        spec=spec(
            "{sftp} delivery",
            ("Files", "One complete file a day."),
            ("Transfers", "Uploads may take up to 10 minutes."),
        ),
        history=history(
            "Truncated export",
            "The partner received a cut-off file.",
            "The upload was interrupted.",
            "The file was sent again.",
            "Sizes are now checked after upload.",
        ),
    ),
    NextFamily(
        number=18,
        name="filename_pattern_changed",
        category="file_transfer",
        group="change",
        descriptions=(
            "{partner} hasn't received today's {domain} export.",
            "The {domain} export hasn't been picked up since about {time}.",
        ),
        failing="sftp",
        error="Pickup found no file matching {domain}_YYYYMMDD.csv; ignored {domain}_YYYYMMDD_HHMMSS.csv",
        exception="PickupError",
        root_cause="A release adds a timestamp to {exporter}'s file names, and {sftp}'s pickup only matches the old pattern, so the files are never picked up.",
        changes=(
            Change(
                "deployment",
                "exporter",
                ("Add a timestamp to export file names",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("redeliver_file", "exporter"),
            ("notify_service_owner", "exporter"),
        ),
        acceptable=("Restore the file name pattern", "Send the export again"),
        unsafe=("Delete files at {sftp}",),
        runbook=runbook(
            "Export not picked up",
            "Use this runbook when {sftp} doesn't pick up the export.",
            [
                "List the files waiting.",
                "Compare their names with the agreed pattern.",
                "Send the file again with the right name.",
            ],
            ["Agree name changes with the partner first."],
        ),
        spec=spec(
            "{sftp} delivery",
            ("Names", "Files must be named {domain}_YYYYMMDD.csv."),
            ("Pickup", "Other names are ignored."),
        ),
        history=history(
            "Export ignored by the partner",
            "The file was never picked up.",
            "The file name didn't match.",
            "The file was renamed and sent again.",
            "Name changes now need the partner's agreement.",
        ),
    ),
    NextFamily(
        number=19,
        name="consumer_group_renamed",
        category="queue_or_event_processing",
        group="change",
        descriptions=(
            "Some {domain} events were never processed since about {time}.",
            "{reports} is missing records since about {time}.",
        ),
        failing="reports",
        error="Reconciliation: {n} events published by {processor} were never processed by {worker}",
        exception="ReconciliationError",
        root_cause="A release renamed {worker}'s consumer group; the new group started at the latest offset, so the messages in between were skipped.",
        changes=(
            Change(
                "deployment",
                "worker",
                ("Rename the consumer group to {domain}-worker-v2",),
            ),
        ),
        extra_logs=(
            (
                "worker",
                "WARN",
                "No committed offset for consumer group {domain}-worker-v2; starting at the latest offset",
                -25,
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=("Reprocess the skipped events", "Restore the consumer group"),
        unsafe=("Reset every offset to the start",),
        runbook=runbook(
            "Events not processed",
            "Use this runbook when events from {processor} are missing downstream.",
            [
                "Compare published and processed counts.",
                "Check the consumer group's offsets.",
                "Reprocess the missing range.",
            ],
            ["Don't reprocess everything."],
        ),
        spec=spec(
            "{queue} consumers",
            ("Groups", "{worker} consumes as one consumer group."),
            ("Offsets", "A new group starts at the latest offset."),
        ),
        history=history(
            "Events skipped",
            "Some events were never processed.",
            "A consumer group started at the latest offset.",
            "The range was reprocessed.",
            "Group changes now copy offsets.",
        ),
    ),
    NextFamily(
        number=20,
        name="visibility_timeout_shortened",
        category="queue_or_event_processing",
        group="change",
        descriptions=(
            "Some {domain} work is being done twice since about {time}.",
            "{worker} reports duplicates since about {time}.",
        ),
        failing="worker",
        error="Message {code} was processed twice: it became visible again before processing finished",
        exception="DuplicateMessage",
        root_cause="A settings change on {queue} shortened the visibility timeout, so messages reappear before {worker} finishes them and are processed twice.",
        changes=(
            Change("deployment", "queue", ("Set the visibility timeout to 10 s",)),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("notify_service_owner", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=("Restore the visibility timeout", "Undo the duplicate work"),
        unsafe=("Turn off message acknowledgements",),
        runbook=runbook(
            "Messages processed twice",
            "Use this runbook when {worker} processes a message twice.",
            [
                "Compare processing time with the visibility timeout.",
                "Restore a timeout longer than the processing time.",
                "Undo the duplicates.",
            ],
            ["Don't delete messages by hand."],
        ),
        spec=spec(
            "{queue} settings",
            ("Visibility", "A received message is hidden for 5 minutes."),
            ("Processing", "{worker} takes up to 2 minutes a message."),
        ),
        history=history(
            "Duplicate processing",
            "Messages were processed twice.",
            "The visibility timeout was shorter than processing.",
            "The timeout was restored.",
            "Queue settings now need a review.",
        ),
    ),
    NextFamily(
        number=21,
        name="ordering_broken_by_concurrency",
        category="queue_or_event_processing",
        group="change",
        descriptions=(
            "{worker} rejects some order updates since about {time}.",
            "Some {domain} updates fail since about {time}.",
        ),
        failing="worker",
        error="Update for order {code} rejected: the order doesn't exist yet",
        exception="NotFoundError",
        root_cause="A release makes {worker} process messages in parallel, so an order's update can arrive before its creation and is rejected.",
        changes=(
            Change(
                "deployment",
                "worker",
                ("Process messages with 8 parallel consumers",),
            ),
        ),
        extra_logs=(("worker", "INFO", "Created order {code}", 1),),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=(
            "Process each order's messages in order",
            "Replay the rejected updates",
        ),
        unsafe=("Drop updates for unknown orders",),
        runbook=runbook(
            "Updates for unknown orders",
            "Use this runbook when {worker} rejects updates for orders it doesn't have.",
            [
                "Check when the order was created.",
                "Check how messages are ordered.",
                "Replay the updates.",
            ],
            ["Keep each order's messages in order."],
        ),
        spec=spec(
            "{queue} order events",
            ("Ordering", "Events for one order are in order within its partition."),
            ("Consumers", "One consumer a partition keeps that order."),
        ),
        history=history(
            "Updates rejected",
            "Updates arrived before their orders.",
            "Messages were processed out of order.",
            "Ordering was restored and the updates replayed.",
            "Parallelism is now per partition.",
        ),
    ),
    NextFamily(
        number=22,
        name="wrong_image_tag",
        category="deployment_or_configuration",
        group="change",
        descriptions=(
            "{processor} is down since about {time}.",
            "{Domain} processing stopped at about {time}.",
        ),
        failing="processor",
        error="Startup failed: unknown flag --seed-dev-data",
        exception="StartupError",
        root_cause="A release deployed a development image of {processor} whose start-up flags don't exist in production, so it won't start.",
        changes=(
            Change("deployment", "processor", ("Deploy image {processor}:dev-{n}",)),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "processor"),
            ("add_monitoring", "processor"),
        ),
        acceptable=("Roll back to the production image", "Replay the missed work"),
        unsafe=("Remove start-up checks",),
        runbook=runbook(
            "{processor} won't start",
            "Use this runbook when {processor} fails at start-up.",
            [
                "Read the start-up error.",
                "Check the image and its settings.",
                "Roll back to the last good image.",
            ],
            ["Deploy only images built for production."],
        ),
        spec=spec(
            "{processor} service",
            ("Image", "Production runs images tagged with a release number."),
            ("Start-up", "Unknown flags stop the service."),
        ),
        history=history(
            "{processor} down",
            "The service failed at start-up.",
            "The wrong image was deployed.",
            "The previous image was restored.",
            "Image tags are now checked before deployment.",
        ),
    ),
    NextFamily(
        number=23,
        name="memory_limit_halved",
        category="deployment_or_configuration",
        group="change",
        descriptions=(
            "{worker} keeps restarting since about {time}.",
            "{Domain} work in {worker} stops and starts since about {time}.",
        ),
        failing="worker",
        error="Container killed: out of memory (limit 256 MiB); restarting",
        exception="OOMKilled",
        root_cause="A release halved {worker}'s memory limit, so it runs out of memory, is killed and restarts in a loop.",
        changes=(
            Change("deployment", "worker", ("Lower the memory limit to 256 MiB",)),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("replay_failed_messages", "worker"),
            ("add_monitoring", "worker"),
        ),
        acceptable=("Restore the memory limit", "Replay the interrupted work"),
        unsafe=("Remove the memory limit",),
        runbook=runbook(
            "{worker} restarts",
            "Use this runbook when {worker} restarts again and again.",
            [
                "Read why the container was stopped.",
                "Compare its memory use with the limit.",
                "Restore a limit that fits.",
            ],
            ["Don't remove limits."],
        ),
        spec=spec(
            "{worker} resources",
            ("Memory", "The worker needs about 400 MiB at peak."),
            ("Limit", "The limit is 512 MiB."),
        ),
        history=history(
            "{worker} restart loop",
            "The worker restarted repeatedly.",
            "Its memory limit was too low.",
            "The limit was restored.",
            "Limit changes now need a load test.",
        ),
    ),
    NextFamily(
        number=24,
        name="cron_schedule_typo",
        category="deployment_or_configuration",
        group="change",
        descriptions=(
            "The {domain} morning report is missing today.",
            "No {domain} report arrived this morning.",
        ),
        failing="reports",
        error="No scheduled run of {reports} started this morning; the next run is set for 18:00",
        exception="MissedRun",
        root_cause="A release set {reports}' schedule to the wrong hour, so the morning report is missing.",
        changes=(
            Change(
                "deployment",
                "reports",
                ("Move the schedule to the new cron format",),
            ),
        ),
        plan=(
            ("rollback_deployment", "CHANGE"),
            ("rerun_job", "reports"),
            ("add_monitoring", "reports"),
        ),
        acceptable=("Restore the schedule", "Run the report now"),
        unsafe=("Run the report every minute",),
        runbook=runbook(
            "Morning report missing",
            "Use this runbook when the morning report isn't produced.",
            [
                "Check whether the job started.",
                "Check its schedule.",
                "Run it and fix the schedule.",
            ],
            ["Don't run the report twice."],
        ),
        spec=spec(
            "{reports} job",
            ("Schedule", "Runs every day at 06:00 UTC."),
            ("Output", "One report a day."),
        ),
        history=history(
            "Morning report missing",
            "The report wasn't produced.",
            "The job's schedule was wrong.",
            "The schedule was fixed and the report run.",
            "Schedules are now checked after deployment.",
        ),
    ),
    # ------------------------------------------- a cause, nothing changed before it
    NextFamily(
        number=25,
        name="clock_drift",
        category="authentication",
        group="nothing_changed",
        descriptions=(
            "{partner} rejects {worker}'s requests since about {time}.",
            "Calls from {worker} to {partner} fail since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 401 Unauthorized: the token is not valid yet",
        exception="AuthenticationError",
        root_cause="The clock on {worker}'s host runs {skew} minutes fast, so {partner} rejects its tokens as not valid yet.",
        extra_logs=(
            (
                "worker",
                "WARN",
                "Local clock is {skew} minutes ahead of {partner}'s Date header",
                1,
            ),
        ),
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=("Correct the host's clock", "Resend the failed calls"),
        unsafe=("Ask {partner} to stop checking token times",),
        runbook=runbook(
            "Tokens rejected as not valid yet",
            "Use this runbook when {partner} says a token is not valid yet.",
            [
                "Compare the host's clock with a time server.",
                "Correct the clock.",
                "Resend the failed calls.",
            ],
            ["Keep every host synchronised."],
        ),
        spec=spec(
            "{partner} tokens",
            (
                "Validity",
                "Tokens are valid from their issue time, with 1 minute of tolerance.",
            ),
            (
                "Errors",
                "401 not valid yet means the token's issue time is in the future.",
            ),
        ),
        history=history(
            "Tokens not valid yet",
            "Calls failed with 401 not valid yet.",
            "A host's clock had drifted.",
            "The clock was corrected.",
            "Clock drift now raises an alert.",
        ),
    ),
    NextFamily(
        number=26,
        name="subscription_lapsed",
        category="authorisation",
        group="nothing_changed",
        descriptions=(
            "{partner} refuses {worker}'s calls since about {time}.",
            "{worker} can't use {partner} since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 403 Forbidden: subscription inactive for this account",
        exception="AccessDenied",
        root_cause="The {partner} account's subscription lapsed, so {partner} refuses {worker}'s calls.",
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=("Renew the subscription", "Resend the refused calls"),
        unsafe=("Use another team's account",),
        runbook=runbook(
            "{partner} answers 403",
            "Use this runbook when {partner} refuses an account.",
            [
                "Read the reason in the response.",
                "Check the account's status with the provider.",
                "Renew or fix the account.",
            ],
            ["Don't borrow another account."],
        ),
        spec=spec(
            "{partner} accounts",
            ("Subscription", "Calls need an active subscription."),
            ("Errors", "403 subscription inactive means the account must be renewed."),
        ),
        history=history(
            "{partner} refused the account",
            "Calls failed with 403.",
            "The subscription had lapsed.",
            "It was renewed.",
            "Renewal dates are now tracked.",
        ),
    ),
    NextFamily(
        number=27,
        name="partner_requires_new_field",
        category="schema_contract_mismatch",
        group="nothing_changed",
        descriptions=(
            "{partner} rejects {worker}'s requests since about {time}.",
            "Orders sent to {partner} fail since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 422 Unprocessable: required field currency is missing",
        exception="ContractViolation",
        root_cause="{partner}'s API started requiring a currency field without notice, so {worker}'s requests without it are rejected.",
        plan=(
            ("update_field_mapping", "worker"),
            ("replay_failed_messages", "worker"),
            ("add_contract_test", "worker"),
        ),
        acceptable=("Send the currency field", "Resend the rejected requests"),
        unsafe=("Send a made-up currency",),
        runbook=runbook(
            "{partner} rejects requests",
            "Use this runbook when {partner} answers 422.",
            [
                "Read which field the provider wants.",
                "Map the field.",
                "Resend the requests.",
            ],
            ["Don't invent values."],
        ),
        spec=spec(
            "{partner} orders API",
            ("Fields", "id, amount and customer are required."),
            ("Errors", "422 lists the fields that are wrong or missing."),
        ),
        history=history(
            "{partner} rejected requests",
            "Requests failed with 422.",
            "The provider required a new field.",
            "The field was added and the requests resent.",
            "Provider changes are now tracked.",
        ),
    ),
    NextFamily(
        number=28,
        name="certificate_expired",
        category="networking",
        group="nothing_changed",
        descriptions=(
            "{worker} can't connect to {partner} since about {time}.",
            "Every call from {worker} to {partner} fails since about {time}.",
        ),
        failing="worker",
        error="TLS handshake with {partner} failed: certificate has expired",
        exception="SSLError",
        root_cause="{partner}'s TLS certificate expired, so {worker}'s connections fail the handshake.",
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=(
            "Ask {partner} to renew its certificate",
            "Resend the failed calls",
        ),
        unsafe=("Turn off certificate checks",),
        runbook=runbook(
            "TLS errors calling {partner}",
            "Use this runbook for TLS handshake failures with {partner}.",
            [
                "Read the handshake error.",
                "Check the provider's certificate dates.",
                "Contact the provider.",
            ],
            ["Never turn off certificate checks."],
        ),
        spec=spec(
            "{partner} endpoint",
            ("TLS", "Connections use TLS 1.2 or later."),
            ("Certificates", "The provider renews its certificate before it expires."),
        ),
        history=history(
            "TLS failures with {partner}",
            "Handshakes failed.",
            "The provider's certificate had expired.",
            "The provider renewed it.",
            "Certificate expiry is now monitored.",
        ),
    ),
    NextFamily(
        number=29,
        name="table_outgrew_query",
        category="timeout",
        group="nothing_changed",
        descriptions=(
            "The {domain} daily report fails since about {time}.",
            "{reports} fails to finish since about {time}.",
        ),
        failing="reports",
        error="Report query on {store} cancelled after 5 s",
        exception="QueryTimeout",
        root_cause="The records table grew until the report query switched to a full scan, so it now takes longer than its 5-second limit.",
        extra_logs=(
            (
                "reports",
                "INFO",
                "Query plan for the daily report: sequential scan on records, {n}000 rows",
                -1,
            ),
        ),
        plan=(("notify_service_owner", "reports"), ("add_monitoring", "reports")),
        acceptable=("Add an index for the report query", "Run the report again"),
        unsafe=("Remove the query timeout",),
        runbook=runbook(
            "Report query times out",
            "Use this runbook when {reports}' query times out.",
            [
                "Read the query plan.",
                "Check the table's size.",
                "Add an index or narrow the query.",
            ],
            ["Don't remove the timeout."],
        ),
        spec=spec(
            "{store} limits",
            ("Timeouts", "Report queries are cancelled after 5 s."),
            ("Indexes", "Records are indexed by id."),
        ),
        history=history(
            "Report query too slow",
            "The query was cancelled after 5 s.",
            "The table outgrew its index.",
            "An index was added.",
            "Table growth is now tracked.",
        ),
    ),
    NextFamily(
        number=30,
        name="daily_quota_exhausted",
        category="rate_limiting",
        group="nothing_changed",
        descriptions=(
            "{partner} refuses calls from {worker} since about {time}.",
            "{worker}'s calls to {partner} fail since about {time}.",
        ),
        failing="worker",
        error="{partner} answered 429: daily quota of {quota} requests exhausted; it resets at 00:00 UTC",
        exception="RateLimitError",
        root_cause="Month-end volume used up {partner}'s daily quota, so {worker}'s later calls are refused until midnight.",
        extra_logs=(
            (
                "worker",
                "INFO",
                "Month-end run: {n} requests sent to {partner} today",
                -10,
            ),
        ),
        plan=(
            ("enable_rate_limiting", "worker"),
            ("replay_failed_messages", "worker"),
            ("notify_service_owner", "worker"),
        ),
        acceptable=(
            "Spread month-end work over the day",
            "Ask {partner} for a higher quota",
        ),
        unsafe=("Use another team's key",),
        runbook=runbook(
            "{partner} daily quota used up",
            "Use this runbook when {partner}'s daily quota runs out.",
            [
                "Check today's request count.",
                "Slow down or defer work.",
                "Resend after the reset.",
            ],
            ["Don't borrow keys."],
        ),
        spec=spec(
            "{partner} limits",
            ("Quota", "{quota} requests a day, reset at 00:00 UTC."),
            ("Errors", "429 with a quota reason means the day's quota is used."),
        ),
        history=history(
            "{partner} quota used up",
            "Calls were refused in the afternoon.",
            "Month-end volume used the quota.",
            "Work was resent after the reset.",
            "Month-end work is now spread out.",
        ),
    ),
    NextFamily(
        number=31,
        name="receiver_stopped_polling",
        category="file_transfer",
        group="nothing_changed",
        descriptions=(
            "{partner} hasn't processed our {domain} files since about {time}.",
            "No acknowledgements from {partner} since about {time}.",
        ),
        failing="exporter",
        error="Files delivered to {sftp} haven't been collected: 4 files waiting, the oldest for 6 hours",
        exception="PickupMissing",
        root_cause="{partner}'s pickup job stopped polling {sftp}, so delivered files are never collected or acknowledged.",
        extra_logs=(
            ("exporter", "INFO", "Delivered {domain}_export.csv to {sftp}", -60),
        ),
        plan=(("notify_service_owner", "exporter"), ("add_monitoring", "exporter")),
        acceptable=("Ask {partner} to restart its pickup", "Leave the files in place"),
        unsafe=("Delete the waiting files",),
        runbook=runbook(
            "Files not collected",
            "Use this runbook when files at {sftp} aren't collected.",
            [
                "List the waiting files.",
                "Ask the provider whether its pickup runs.",
                "Keep the files until they're collected.",
            ],
            ["Don't resend files that are waiting."],
        ),
        spec=spec(
            "{sftp} delivery",
            ("Pickup", "The provider collects files every 15 minutes."),
            ("Acknowledgement", "Each collected file is acknowledged."),
        ),
        history=history(
            "Files not collected",
            "Files waited for hours.",
            "The provider's pickup had stopped.",
            "The provider restarted it.",
            "Waiting files now raise an alert.",
        ),
    ),
    NextFamily(
        number=32,
        name="poison_message",
        category="queue_or_event_processing",
        group="nothing_changed",
        descriptions=(
            "{Domain} processing is stuck since about {time}.",
            "{worker} isn't making progress since about {time}.",
        ),
        failing="worker",
        error="Message at offset {n} failed to parse; retrying (attempt 40)",
        exception="ParseError",
        root_cause="One malformed message fails and is retried forever, so its partition makes no progress.",
        extra_logs=(
            (
                "worker",
                "WARN",
                "Partition 3 has made no progress past offset {n} for 20 minutes",
                15,
            ),
        ),
        plan=(("notify_service_owner", "worker"), ("add_monitoring", "worker")),
        acceptable=("Move the bad message aside", "Let the partition continue"),
        unsafe=("Skip the whole partition",),
        runbook=runbook(
            "A partition is stuck",
            "Use this runbook when a partition stops making progress.",
            [
                "Find the offset that keeps failing.",
                "Move that message to the dead-letter queue.",
                "Check the partition catches up.",
            ],
            ["Don't skip more than the bad message."],
        ),
        spec=spec(
            "{queue} processing",
            ("Retries", "A failing message is retried."),
            ("Dead letters", "Messages can be moved to the dead-letter queue."),
        ),
        history=history(
            "Partition stuck",
            "One partition stopped making progress.",
            "A malformed message was retried forever.",
            "It was moved aside.",
            "Retries are now limited.",
        ),
    ),
    # --------------------------------------------------------- no diagnosable cause
    NextFamily(
        number=33,
        name="sporadic_partner_502s",
        category="unknown",
        group="no_cause",
        descriptions=(
            "{worker} logged a few errors calling {partner} today.",
            "Someone noticed occasional errors from {partner} in {worker}'s logs.",
        ),
        failing="worker",
        error="{partner} answered 502 Bad Gateway",
        exception="HTTPError",
        root_cause=NO_CAUSE_ROOT.format(
            what="a few 502 responses over several hours, each of which succeeded when retried."
        ),
        pattern="scattered",
        recovery="Retried the request to {partner}; it succeeded",
        runbook=runbook(
            "Occasional errors from {partner}",
            "Use this runbook for occasional error responses from {partner}.",
            ["Check the error rate.", "Check that retries succeed."],
            ["Don't change anything for isolated errors."],
        ),
        spec=spec(
            "{partner} API",
            ("Errors", "Occasional 5xx responses are expected; clients retry."),
        ),
        history=history(
            "Occasional errors from {partner}",
            "A few calls failed and succeeded on retry.",
            "No cause was found.",
            "No action was needed.",
            "The error rate is watched.",
        ),
    ),
    NextFamily(
        number=34,
        name="one_slow_export",
        category="unknown",
        group="no_cause",
        descriptions=(
            "Last night's {domain} export was slow.",
            "The {domain} export took much longer than usual last night.",
        ),
        failing="exporter",
        error="Nightly export took 74 minutes; it usually takes about 25",
        exception=None,
        root_cause=NO_CAUSE_ROOT.format(
            what="one night's export was slow, and the next night's was normal."
        ),
        pattern="once",
        level="WARN",
        recovery="Nightly export took 24 minutes",
        runbook=runbook(
            "Slow export",
            "Use this runbook when the export is slow.",
            ["Compare with previous nights.", "Look for a pattern before acting."],
            ["Don't change the export for one slow night."],
        ),
        spec=spec(
            "{exporter} job", ("Duration", "The export usually takes 20 to 30 minutes.")
        ),
        history=history(
            "Slow export",
            "One export was slow.",
            "No cause was found.",
            "The next run was normal.",
            "Durations are watched.",
        ),
    ),
    NextFamily(
        number=35,
        name="scattered_401s",
        category="unknown",
        group="no_cause",
        descriptions=(
            "{worker} logged a few 401s from {partner} today.",
            "There were some authentication errors from {partner} today.",
        ),
        failing="worker",
        error="{partner} answered 401 Unauthorized",
        exception="AuthenticationError",
        root_cause=NO_CAUSE_ROOT.format(
            what="a handful of 401s over a day, and the same tokens were accepted on retry."
        ),
        pattern="scattered",
        recovery="Retried with the same token; {partner} accepted it",
        runbook=runbook(
            "Occasional 401s from {partner}",
            "Use this runbook for occasional 401 responses.",
            ["Check whether retries with the same token succeed.", "Watch the rate."],
            ["Don't rotate credentials for isolated errors."],
        ),
        spec=spec("{partner} access", ("Tokens", "Tokens are valid for one hour.")),
        history=history(
            "Occasional 401s",
            "A few calls got 401 and succeeded on retry.",
            "No cause was found.",
            "No action was needed.",
            "The rate is watched.",
        ),
    ),
    NextFamily(
        number=36,
        name="self_clearing_backlog",
        category="unknown",
        group="no_cause",
        descriptions=(
            "{queue} had a backlog this afternoon.",
            "Someone saw a queue backlog for {worker} today.",
        ),
        failing="worker",
        error="Backlog on {queue} reached 4,200 messages",
        exception=None,
        root_cause=NO_CAUSE_ROOT.format(
            what="a short backlog that cleared by itself, with no rise in incoming messages."
        ),
        pattern="once",
        level="WARN",
        recovery="Backlog on {queue} back to normal; incoming rate unchanged at about 300 a minute",
        recovery_after=40,
        runbook=runbook(
            "Queue backlog",
            "Use this runbook for a backlog on {queue}.",
            ["Check whether it is clearing.", "Compare the incoming rate."],
            ["Don't scale up for a backlog that is clearing."],
        ),
        spec=spec(
            "{queue} processing",
            ("Throughput", "{worker} handles about 400 messages a minute."),
        ),
        history=history(
            "Short backlog",
            "A backlog built up and cleared.",
            "No cause was found.",
            "No action was needed.",
            "Backlogs are watched.",
        ),
    ),
    NextFamily(
        number=37,
        name="single_wrong_total",
        category="unknown",
        group="no_cause",
        descriptions=(
            "A customer says their {domain} total was wrong.",
            "One customer complained about a wrong total.",
        ),
        failing="processor",
        error="A customer reported a wrong total for order {code}",
        exception=None,
        root_cause=NO_CAUSE_ROOT.format(
            what="one customer reported a wrong total that the stored data doesn't reproduce."
        ),
        pattern="once",
        level="WARN",
        recovery="Recomputed order {code}: the stored total matches the order lines",
        recovery_after=15,
        runbook=runbook(
            "A customer reports a wrong total",
            "Use this runbook when a customer disputes a total.",
            ["Recompute the order.", "Look for other cases before acting."],
            ["Don't change totals without evidence."],
        ),
        spec=spec(
            "{processor} orders",
            ("Totals", "The total is the sum of the order lines and tax."),
        ),
        history=history(
            "Disputed total",
            "A customer reported a wrong total.",
            "The stored data was correct.",
            "The customer was answered.",
            "None.",
        ),
    ),
    NextFamily(
        number=38,
        name="dns_blips",
        category="unknown",
        group="no_cause",
        descriptions=(
            "Several {domain} services logged DNS errors this morning.",
            "There were DNS errors in {domain} for a minute.",
        ),
        failing="worker",
        error="DNS lookup for {partner} failed: SERVFAIL",
        exception="DNSError",
        root_cause=NO_CAUSE_ROOT.format(
            what="a few DNS lookups failed across services within one minute, then none."
        ),
        gap=(5, 15),
        extra_logs=(
            ("processor", "ERROR", "DNS lookup for {store} failed: SERVFAIL", 0),
            ("exporter", "ERROR", "DNS lookup for {sftp} failed: SERVFAIL", 1),
            ("worker", "INFO", "DNS lookups succeeding again", 2),
        ),
        runbook=runbook(
            "DNS errors",
            "Use this runbook for DNS lookup failures.",
            ["Check whether they continue.", "Check the resolver's status."],
            ["Don't change DNS settings for a blip."],
        ),
        spec=spec(
            "{domain} network", ("DNS", "Services use the platform's resolvers.")
        ),
        history=history(
            "DNS blip",
            "Lookups failed for a minute.",
            "No cause was found.",
            "No action was needed.",
            "Resolver errors are watched.",
        ),
    ),
    NextFamily(
        number=39,
        name="one_duplicate_notification",
        category="unknown",
        group="no_cause",
        descriptions=(
            "A customer got the same {domain} notification twice.",
            "One customer received a duplicate notification.",
        ),
        failing="worker",
        error="Customer {n} received notification {code} twice",
        exception=None,
        root_cause=NO_CAUSE_ROOT.format(
            what="one customer got one notification twice, with no other duplicates and no errors."
        ),
        pattern="once",
        level="WARN",
        recovery="Checked the last 24 hours: no other duplicate notifications",
        recovery_after=5,
        runbook=runbook(
            "Duplicate notification",
            "Use this runbook when a customer gets a notification twice.",
            ["Check for other duplicates.", "Look for errors around the time."],
            ["Don't change delivery for one duplicate."],
        ),
        spec=spec(
            "{worker} notifications",
            ("Delivery", "Notifications are sent at least once."),
        ),
        history=history(
            "Duplicate notification",
            "One customer got a notification twice.",
            "No cause was found.",
            "No action was needed.",
            "None.",
        ),
    ),
    NextFamily(
        number=40,
        name="late_report_once",
        category="unknown",
        group="no_cause",
        descriptions=(
            "The {domain} morning report was late today.",
            "Today's {domain} report arrived late.",
        ),
        failing="reports",
        error="The morning report finished 40 minutes late; no errors were logged",
        exception=None,
        root_cause=NO_CAUSE_ROOT.format(
            what="the morning report finished 40 minutes late once, with no errors."
        ),
        pattern="once",
        level="WARN",
        recovery="The morning report finished on time",
        runbook=runbook(
            "Late report",
            "Use this runbook when the morning report is late.",
            ["Check whether it happened before.", "Look for errors."],
            ["Don't change the schedule for one late run."],
        ),
        spec=spec("{reports} job", ("Schedule", "The report is due by 06:30 UTC.")),
        history=history(
            "Late report",
            "The report was late once.",
            "No cause was found.",
            "No action was needed.",
            "Lateness is watched.",
        ),
    ),
)
