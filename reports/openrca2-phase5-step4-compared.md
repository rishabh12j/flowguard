# Phase 5, step 4: the kind check, second version, against the first

Output of the comparison script, 2026-11-16. Columns of the first table: system, cases, lead and survey, first version drafts, first version finals, second version drafts, second version finals, spread run, standard agent on the fixed tool.

```
== exact: system | n | ls | kind drafts | kind | kind2 drafts | kind2 | spread | base3
hs 33 28 24 25 28 31 27 30
otel-demo 7 4 5 4 3 6 5 4
ts 60 30 31 43 29 34 34 20
all 100 62 60 72 60 71 66 54
kind2 vs kind (won, lost, p): (11, 12, 1)
kind2 drafts->finals (fixed, broken): 16 5
kind  drafts->finals (fixed, broken): 16 4

== verdicts kind
  DISAGREED draft R verdict W lead kept 5
  DISAGREED draft R verdict W lead took 5
  DISAGREED draft W verdict R lead kept 2
  DISAGREED draft W verdict R lead took 16
  DISAGREED draft W verdict W lead kept 1
  DISAGREED draft W verdict W lead took 6
  agreed, draft right 61
  agreed, draft wrong 10
  service not a fault 6

== verdicts kind2
  DISAGREED draft R verdict W lead kept 1
  DISAGREED draft R verdict W lead took 5
  DISAGREED draft W verdict R lead kept 7
  DISAGREED draft W verdict R lead took 14
  DISAGREED draft W verdict W lead kept 2
  DISAGREED draft W verdict W lead took 7
  agreed, draft right 61
  agreed, draft wrong 5
  service not a fault 9

== cases where kind and kind2 finals differ
case-059 otel-demo kind 1->0 kind2 1->1 truth [('productcatalog', 'pod_unavailable', 'required')]
    kind  draft [('product-catalog', 'pod_unavailable')] final [('product-catalog', 'network_partition')] verdicts [('pod_unavailable', 'network_partition')]
    kind2 draft [('product-catalog', 'pod_unavailable')] final [('product-catalog', 'pod_unavailable')] verdicts [('pod_unavailable', 'network_partition')]
case-092 ts kind 1->1 kind2 1->0 truth [('tspreserveservice', 'http_aborted', 'required')]
    kind  draft [('ts-preserve-service', 'http_aborted')] final [('ts-preserve-service', 'http_aborted')] verdicts [('http_aborted', 'http_aborted')]
    kind2 draft [('ts-preserve-service', 'http_aborted')] final [('ts-preserve-service', 'network_partition')] verdicts [('http_aborted', 'network_partition')]
case-125 ts kind 0->1 kind2 0->0 truth [('mysql', 'network_partition', 'required')]
    kind  draft [('ts-config-service', 'database_call_failed')] final [('ts-config-service', 'network_partition')] verdicts [('database_call_failed', 'network_partition')]
    kind2 draft [('ts-config-service', 'database_call_failed')] final [('ts-config-service', 'database_call_failed')] verdicts [('database_call_failed', 'network_partition')]
case-146 ts kind 0->1 kind2 0->0 truth [('tsrouteplanservice', 'wrong_return_value', 'not_effective'), ('mysql', 'network_loss', 'required')]
    kind  draft [('ts-route-service', 'database_call_slow')] final [('ts-route-service', 'network_loss')] verdicts [('database_call_slow', 'network_loss')]
    kind2 draft [('ts-route-service', 'database_call_slow')] final [('ts-route-service', 'database_call_slow')] verdicts [('database_call_slow', 'database_call_slow')]
case-170 ts kind 1->1 kind2 0->0 truth [('tstravelplanservice', 'http_slow', 'required')]
    kind  draft [('ts-travel-plan-service', 'http_slow')] final [('ts-travel-plan-service', 'http_slow')] verdicts [('http_slow', 'http_slow')]
    kind2 draft [('ts-route-service', 'jvm_gc_thrashing')] final [('ts-route-service', 'jvm_gc_thrashing')] verdicts [('jvm_gc_thrashing', 'jvm_gc_thrashing')]
case-171 otel-demo kind 0->0 kind2 0->1 truth [('shipping', 'pod_unavailable', 'required'), ('cart', 'container_cpu_saturated', 'optional')]
    kind  draft [('shipping', 'pod_unavailable'), ('frontend', 'dns_lookup_failed')] final [('checkout', 'http_aborted'), ('frontend', 'dns_lookup_failed')] verdicts [('pod_unavailable', 'http_aborted'), ('dns_lookup_failed', 'dns_lookup_failed')]
    kind2 draft [('shipping', 'pod_unavailable'), ('frontend', 'dns_lookup_failed')] final [('shipping', 'pod_unavailable')] verdicts [('pod_unavailable', 'pod_unavailable'), ('dns_lookup_failed', 'network_partition')]
case-194 hs kind 0->0 kind2 0->1 truth [('geo', 'network_delay', 'required'), ('rate', 'container_cpu_saturated', 'optional')]
    kind  draft [('search', 'http_slow')] final [('search', 'network_partition')] verdicts [('http_slow', 'network_partition')]
    kind2 draft [('search', 'http_slow')] final [('search', 'network_delay')] verdicts [('http_slow', 'network_delay')]
case-195 ts kind 0->0 kind2 0->1 truth [('tstravel2service', 'application_method_slow', 'required')]
    kind  draft [('ts-travel2-service', 'application_method_slow'), ('ts-contacts-service', 'application_method_slow')] final [('ts-travel2-service', 'application_method_slow'), ('ts-contacts-service', 'application_method_slow')] verdicts [('application_method_slow', 'application_method_slow'), ('application_method_slow', 'application_method_slow')]
    kind2 draft [('ts-travel2-service', 'http_slow')] final [('ts-travel2-service', 'application_method_slow')] verdicts [('http_slow', 'application_method_slow')]
case-216 ts kind 0->1 kind2 0->0 truth [('tsbasicservice', 'wrong_return_value', 'not_effective'), ('mysql', 'network_partition', 'required')]
    kind  draft [('ts-station-service', 'database_call_failed')] final [('ts-station-service', 'network_partition')] verdicts [('database_call_failed', 'network_partition')]
    kind2 draft [('ts-station-service', 'database_call_failed')] final [('ts-station-service', 'database_call_failed')] verdicts [('database_call_failed', 'network_partition')]
case-226 ts kind 1->1 kind2 0->0 truth [('tsadminuserservice', 'wrong_return_value', 'not_effective'), ('tsauthservice', 'network_loss', 'required')]
    kind  draft [('ts-user-service', 'network_loss')] final [('ts-user-service', 'network_loss')] verdicts [('network_loss', 'network_loss')]
    kind2 draft [('ts-auth-service', 'application_method_slow')] final [('ts-auth-service', 'application_method_slow')] verdicts [('application_method_slow', 'application_method_slow')]
case-235 ts kind 1->1 kind2 0->0 truth [('tsseatservice', 'http_slow', 'required')]
    kind  draft [('ts-seat-service', 'http_slow')] final [('ts-seat-service', 'http_slow')] verdicts [('http_slow', 'http_slow')]
    kind2 draft [('ts-seat-service', 'application_method_slow')] final [('ts-seat-service', 'network_delay')] verdicts [('application_method_slow', 'network_delay')]
case-256 ts kind 1->1 kind2 1->0 truth [('tsauthservice', 'http_response_body_corrupted', 'required')]
    kind  draft [('ts-auth-service', 'http_response_body_corrupted')] final [('ts-auth-service', 'http_response_body_corrupted')] verdicts [('http_response_body_corrupted', 'http_response_body_corrupted')]
    kind2 draft [('ts-auth-service', 'http_response_body_corrupted')] final [('ts-auth-service', 'network_corrupt')] verdicts [('http_response_body_corrupted', 'network_corrupt')]
case-258 ts kind 0->0 kind2 1->1 truth [('tspreserveservice', 'http_aborted', 'required')]
    kind  draft [('ts-preserve-service', 'http_aborted'), ('ts-travel-service', 'http_slow')] final [('ts-preserve-service', 'http_aborted'), ('ts-basic-service', 'network_delay')] verdicts [('http_aborted', 'network_partition'), ('http_slow', 'network_delay')]
    kind2 draft [('ts-preserve-service', 'http_aborted')] final [('ts-preserve-service', 'http_aborted')] verdicts [('http_aborted', 'http_aborted')]
case-267 ts kind 1->1 kind2 0->0 truth [('tstravelservice', 'http_wrong_status_code', 'required')]
    kind  draft [('ts-travel-service', 'http_wrong_status_code')] final [('ts-travel-service', 'http_wrong_status_code')] verdicts [('http_wrong_status_code', 'http_wrong_status_code')]
    kind2 draft [('ts-travel-service', 'http_wrong_status_code'), ('ts-route-plan-service', 'http_slow')] final [('ts-travel-service', 'http_wrong_status_code'), ('ts-route-plan-service', 'http_slow')] verdicts [('http_wrong_status_code', 'http_wrong_status_code'), ('http_slow', 'network_delay')]
case-274 ts kind 0->1 kind2 0->0 truth [('mysql', 'network_partition', 'required')]
    kind  draft [('ts-order-other-service', 'database_call_failed')] final [('ts-order-other-service', 'network_loss')] verdicts [('database_call_failed', 'network_loss')]
    kind2 draft [('ts-order-other-service', 'database_call_failed')] final [('ts-order-other-service', 'database_call_failed')] verdicts [('database_call_failed', 'network_partition')]
case-311 hs kind 0->0 kind2 0->1 truth [('hotelreservrate', 'network_partition', 'required'), ('geo', 'container_memory_saturated', 'optional')]
    kind  draft [('search', 'dns_lookup_failed')] final [('search', 'dns_lookup_failed')] verdicts [('dns_lookup_failed', 'dns_lookup_failed')]
    kind2 draft [('rate', 'pod_unavailable')] final [('rate', 'network_partition')] verdicts [('pod_unavailable', 'network_partition')]
case-337 hs kind 1->0 kind2 1->1 truth [('geo', 'network_delay', 'required'), ('profile', 'container_memory_saturated', 'optional')]
    kind  draft [('search', 'network_delay')] final [('search', 'network_loss')] verdicts [('network_delay', 'network_loss')]
    kind2 draft [('geo', 'network_delay')] final [('geo', 'network_delay')] verdicts [('network_delay', 'network_delay')]
case-339 ts kind 0->1 kind2 0->0 truth [('mysql', 'network_delay', 'required')]
    kind  draft [('ts-consign-service', 'database_call_slow')] final [('ts-consign-service', 'network_delay')] verdicts [('database_call_slow', 'network_delay')]
    kind2 draft [('ts-consign-service', 'database_call_slow')] final [('ts-consign-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_delay')]
case-340 ts kind 0->0 kind2 0->1 truth [('mysql', 'network_loss', 'required')]
    kind  draft [('ts-train-service', 'database_call_slow')] final [('ts-train-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_loss')]
    kind2 draft [('ts-train-service', 'database_call_slow')] final [('ts-train-service', 'network_loss')] verdicts [('database_call_slow', 'network_loss')]
case-359 hs kind 0->0 kind2 1->1 truth [('user', 'pod_unavailable', 'required'), ('attractions', 'container_cpu_saturated', 'required')]
    kind  draft [('user', 'pod_unavailable')] final [('user', 'pod_unavailable')] verdicts [('pod_unavailable', 'pod_unavailable')]
    kind2 draft [('user', 'pod_unavailable'), ('attractions', 'container_cpu_saturated')] final [('user', 'pod_unavailable'), ('attractions', 'container_cpu_saturated')] verdicts [('pod_unavailable', 'pod_unavailable'), ('container_cpu_saturated', 'container_cpu_saturated')]
case-387 ts kind 1->1 kind2 1->0 truth [('tstravelservice', 'http_slow', 'required')]
    kind  draft [('ts-travel-service', 'http_slow')] final [('ts-travel-service', 'http_slow')] verdicts [('http_slow', 'http_slow')]
    kind2 draft [('ts-travel-service', 'http_slow')] final [('ts-travel-service', 'network_delay')] verdicts [('http_slow', 'network_delay')]
case-414 hs kind 0->0 kind2 1->1 truth [('hotelreservrate', 'network_delay', 'required')]
    kind  draft [('search', 'http_slow')] final [('search', 'http_slow')] verdicts [('http_slow', 'network_delay')]
    kind2 draft [('search', 'network_delay')] final [('search', 'network_delay')] verdicts [('network_delay', 'network_delay')]
case-434 hs kind 0->0 kind2 0->1 truth [('hotelreservrate', 'network_delay', 'required'), ('geo', 'container_memory_saturated', 'optional')]
    kind  draft [('search', 'http_slow')] final [('search', 'network_loss')] verdicts [('http_slow', 'network_loss')]
    kind2 draft [('search', 'http_slow')] final [('search', 'network_delay')] verdicts [('http_slow', 'network_delay')]

== kind2 cases moved by the check
case-011 ts 0->1 truth [('tsrouteplanservice', 'wrong_return_value', 'not_effective'), ('mysql', 'network_loss', 'required')] draft [('ts-route-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_loss', 'low')] final [('ts-route-service', 'network_loss')]
case-036 hs 1->0 truth [('geo', 'container_cpu_saturated', 'required')] draft [('geo', 'container_cpu_saturated')] verdicts [('container_cpu_saturated', 'process_cpu_saturated', 'low')] final [('geo', 'process_cpu_saturated')]
case-092 ts 1->0 truth [('tspreserveservice', 'http_aborted', 'required')] draft [('ts-preserve-service', 'http_aborted')] verdicts [('http_aborted', 'network_partition', 'low')] final [('ts-preserve-service', 'network_partition')]
case-124 ts 0->1 truth [('mysql', 'network_partition', 'required')] draft [('ts-train-service', 'database_call_failed')] verdicts [('database_call_failed', 'network_partition', 'medium')] final [('ts-train-service', 'network_partition')]
case-126 hs 0->1 truth [('hotelreservrate', 'network_delay', 'required')] draft [('search', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('search', 'network_delay')]
case-154 ts 0->1 truth [('mysql', 'network_loss', 'required')] draft [('ts-price-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_loss', 'medium')] final [('ts-price-service', 'network_loss')]
case-155 otel-demo 0->1 truth [('checkout', 'network_delay', 'required'), ('quote', 'pod_failure', 'optional')] draft [('checkout', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('checkout', 'network_delay')]
case-171 otel-demo 0->1 truth [('shipping', 'pod_unavailable', 'required'), ('cart', 'container_cpu_saturated', 'optional')] draft [('shipping', 'pod_unavailable'), ('frontend', 'dns_lookup_failed')] verdicts [('pod_unavailable', 'pod_unavailable', 'medium'), ('dns_lookup_failed', 'network_partition', 'low')] final [('shipping', 'pod_unavailable')]
case-194 hs 0->1 truth [('geo', 'network_delay', 'required'), ('rate', 'container_cpu_saturated', 'optional')] draft [('search', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('search', 'network_delay')]
case-195 ts 0->1 truth [('tstravel2service', 'application_method_slow', 'required')] draft [('ts-travel2-service', 'http_slow')] verdicts [('http_slow', 'application_method_slow', 'medium')] final [('ts-travel2-service', 'application_method_slow')]
case-208 ts 0->1 truth [('tsadminorderservice', 'wrong_return_value', 'not_effective'), ('mysql', 'network_loss', 'required')] draft [('ts-order-other-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_loss', 'medium')] final [('ts-order-other-service', 'network_loss')]
case-256 ts 1->0 truth [('tsauthservice', 'http_response_body_corrupted', 'required')] draft [('ts-auth-service', 'http_response_body_corrupted')] verdicts [('http_response_body_corrupted', 'network_corrupt', 'low')] final [('ts-auth-service', 'network_corrupt')]
case-296 ts 0->1 truth [('tsrouteplanservice', 'wrong_return_value', 'not_effective'), ('mysql', 'network_loss', 'required')] draft [('ts-route-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_loss', 'medium')] final [('ts-route-service', 'network_loss')]
case-300 ts 0->1 truth [('tsorderotherservice', 'network_delay', 'required')] draft [('ts-seat-service', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('ts-seat-service', 'network_delay')]
case-311 hs 0->1 truth [('hotelreservrate', 'network_partition', 'required'), ('geo', 'container_memory_saturated', 'optional')] draft [('rate', 'pod_unavailable')] verdicts [('pod_unavailable', 'network_partition', 'medium')] final [('rate', 'network_partition')]
case-329 ts 0->1 truth [('tstravelplanservice', 'wrong_return_value', 'not_effective'), ('tsconfigservice', 'network_partition', 'required')] draft [('ts-seat-service', 'application_method_slow')] verdicts [('application_method_slow', 'network_partition', 'medium')] final [('ts-seat-service', 'network_partition')]
case-340 ts 0->1 truth [('mysql', 'network_loss', 'required')] draft [('ts-train-service', 'database_call_slow')] verdicts [('database_call_slow', 'network_loss', 'medium')] final [('ts-train-service', 'network_loss')]
case-387 ts 1->0 truth [('tstravelservice', 'http_slow', 'required')] draft [('ts-travel-service', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('ts-travel-service', 'network_delay')]
case-398 otel-demo 0->1 truth [('payment', 'pod_unavailable', 'required'), ('currency', 'container_cpu_saturated', 'optional')] draft [('payment', 'pod_unavailable'), ('frontend', 'dns_lookup_failed')] verdicts [('pod_unavailable', 'pod_unavailable', 'high'), ('dns_lookup_failed', 'pod_unavailable', 'low')] final [('payment', 'pod_unavailable')]
case-434 hs 0->1 truth [('hotelreservrate', 'network_delay', 'required'), ('geo', 'container_memory_saturated', 'optional')] draft [('search', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('search', 'network_delay')]
case-442 ts 1->0 truth [('tstravelplanservice', 'http_slow', 'required')] draft [('ts-travel-plan-service', 'http_slow')] verdicts [('http_slow', 'network_delay', 'medium')] final [('ts-travel-plan-service', 'network_delay')]

cost 4.57 checks 1.38 edge_f1 0.845 kind edge_f1 0.815
notes []
verdict notes []
```
