# Feature Roadmap

## Current implementation status

Audited on **October 22, 2026** against the public SDK's client interfaces,
driver contracts, provider implementations, and checked-in tests. This is an
implementation inventory, not a claim that every parameter has identical
semantics on every provider or that all operations were live-tested during
this documentation review.

**Supported** = implemented; **Conditional** = implemented with the requirements
noted below; **Unsupported** = explicitly rejected by this provider;
**Not exposed** = absent from the public client. Ali provider packages remain
placeholders and are planned, not implemented, for Blob Storage, STS, and Pub/Sub.

## Blob Storage (`BucketClient`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `upload` | Upload bytes or a binary stream | Supported | Supported |
| `upload_from_path` | Upload from a local file | Supported | Supported |
| `download` | Download object content | Supported | Supported |
| `download_to_path` | Download to a local path | Supported | Supported |
| `download_to_file` | Download to a binary file | Supported | Supported |
| `download_stream` | Iterate content chunks | Supported | Supported |
| `delete` | Delete one object | Supported | Supported |
| `delete_objects` | Delete multiple objects | Supported | Supported |
| `copy` | Copy to another bucket | Supported | Supported |
| `copy_from` | Copy from another bucket | Supported | Supported |
| `list_page` | List with prefix, delimiter, and pagination | Supported | Supported |
| `does_object_exist` | Check object existence | Supported | Supported |
| `does_bucket_exist` | Check bucket existence | Supported | Supported |
| `get_metadata` | Read object metadata | Supported | Supported |
| `get_tags` | Read tags | Supported | Supported |
| `set_tags` | Replace tags | Supported | Supported |
| `get_object_lock` | Read retention and legal hold | Supported | Supported |
| `update_object_retention` | Update retention | Supported | Supported |
| `update_legal_hold` | Update legal hold | Supported | Supported |
| `generate_presigned_url` | Generate a signed upload or download URL | Supported | Supported |
| `list_blob_versions` | List object versions | Supported | Supported |
| `initiate_multipart_upload` | Start a multipart upload | Supported | Supported |
| `upload_part` | Upload a part | Supported | Supported |
| `complete_multipart_upload` | Complete a multipart upload | Supported | Supported |
| `list_parts` | List uploaded parts | Supported | Supported |
| `abort_multipart_upload` | Abort a multipart upload | Supported | Supported |

Read the [Blob Storage guide](guides/blobstore-guide.md) and
[API reference](api/blob.md) for parameters and return types.

- Object lock requires appropriately configured resources and permissions.
- Conditional writes differ: AWS rejects a standalone `if_version_match`;
  GCP rejects a standalone `if_match` for writes. When both are supplied,
  each provider uses its supported token and ignores the redundant one.
- Version ordering is provider-native. Use `is_latest` or explicitly sort
  `last_modified` when ordering matters.
- Resource existence and operation availability do not imply an account has
  permission to perform the operation.

### Async Blob Storage (`AsyncBucketClient`)

The async client implements the same operation names listed above, plus the
directory helpers below. Most operations are awaited; `list_blob_versions`
returns an async iterator directly and is consumed with
`async for version in client.list_blob_versions(key)`, without `await` on the
iterator itself. Use `async with` for cleanup. The same provider preconditions
and resource configuration requirements apply.

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `upload_directory` | Upload local directory contents | Supported | Supported |
| `download_directory` | Download objects under a prefix | Supported | Supported |
| `delete_directory` | Delete objects under a prefix | Supported | Supported |

## STS (`StsClient`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `get_caller_identity` | Identify the caller | Supported | Conditional |
| `assume_role` | Obtain temporary role credentials | Supported | Supported |
| `get_access_token` | Obtain refreshed or scoped credentials | Conditional | Conditional |
| `generate_service_account_token` | Impersonate a service account | Unsupported | Supported |
| `assume_role_with_web_identity` | Exchange a web-identity token | Supported | Supported |

GCP caller-identity and audience-targeted tokens require a compatible service
account or impersonated credential; user OAuth credentials do not support these
ID-token paths. Scoped GCP access tokens require a service-account email. AWS
`get_access_token` uses session-token credentials and ignores `audience` and
`scopes`. GCP `assume_role` impersonates a service account and ignores
`session_name`, `external_id`, `policy`, and `tags`; its `credential_scope`
path supports downscoping. Token lifetimes and trust/impersonation permissions remain
provider-specific. See the [STS guide](guides/sts-guide.md).

### STS utilities (`StsUtilities`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `create_signed_auth_request` | Create a signed caller-identity authentication request | Supported | Unsupported |

## IAM (`IamClient`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `create_identity` | Create or resolve an identity | Supported | Supported |
| `get_identity` | Read its identifier | Supported | Supported |
| `delete_identity` | Delete an identity | Supported | Supported |
| `attach_inline_policy` | Attach policy permissions | Supported | Conditional |
| `get_inline_policy_details` | Read a policy document or binding | Supported | Conditional |
| `get_attached_policies` | List attached policy names or roles | Supported | Conditional |
| `remove_policy` | Remove policy permissions | Supported | Conditional |

GCP represents policy attachments as project IAM role bindings, not named
inline policy documents. Its attachment implementation applies ALLOW statements;
DENY statements are skipped, conditions on translated ALLOW statements are
rejected, and statement resources do not restrict the binding. Do not use
resource entries to constrain access on GCP. Policy lookup/removal uses role names such as
`roles/storage.objectViewer`, rather than the original `PolicyDocument.name`.
Creation options and trust configuration also have provider-specific effects.
See the [IAM guide](guides/iam-guide.md) for the mapping and examples.

## PubSub (`TopicClient` / `SubscriptionClient`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `send` | Publish a message (TopicClient) | Supported | Supported |
| `receive` | Receive a message (SubscriptionClient) | Supported | Supported |
| `send_ack` | Acknowledge one message | Supported | Supported |
| `send_acks` | Batch acknowledgments; returns a Future | Supported | Supported |
| `send_nack` | Make one message available for redelivery | Supported | Supported |
| `send_nacks` | Batch negative acknowledgments; returns a Future | Supported | Supported |
| `can_nack` | Check negative-acknowledgment capability | Supported | Supported |
| `get_attributes` | Read subscription metadata | Supported | Supported |
| `is_retryable` | Classify a failure for retry | Supported | Supported |

These operations are implemented, rather than merely defined as interfaces.
AWS publishing selects `awssns` or `awssqs`; AWS subscriptions use `aws`.
GCP uses `gcp`. Negative acknowledgments and visibility/deadline limits follow
provider semantics. `get_attributes` does not guarantee a backlog count: the
current implementations leave `approximate_number_of_messages` unset.
`is_retryable` classifies an error; it does not promise automatic retry of
every failed operation. See the [Pub/Sub guide](guides/pubsub-guide.md).

## Document Store (`DocStoreClient`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `actions` | Build a list of document actions | Supported | Supported |
| `create` | Create a document | Supported | Supported |
| `replace` | Replace an existing document | Supported | Supported |
| `put` | Upsert a document | Supported | Supported |
| `delete` | Delete a document | Supported | Supported |
| `get` | Read into a supplied document | Supported | Supported |
| `batch_get` | Read multiple documents | Supported | Supported |
| `batch_put` | Upsert multiple documents | Supported | Supported |
| `batch_delete` | Delete multiple documents | Supported | Supported |

### Action-list interface (`ActionList`)

| API | Description | AWS | GCP |
| --- | --- | --- | --- |
| `create` | Queue a create | Supported | Supported |
| `replace` | Queue a replacement | Supported | Supported |
| `put` | Queue an upsert | Supported | Supported |
| `delete` | Queue a delete | Supported | Supported |
| `get` | Queue a read with optional field paths | Supported | Supported |
| `enable_atomic_writes` | Request transactional writes | Supported | Supported |
| `before_do` | Register a before-operation hook | Supported | Supported |
| `run` | Execute the action list | Supported | Supported |

Revision checks, supported field shapes, transaction limits, and atomic-write
constraints depend on the provider. Query/filter/order/pagination APIs are
**not exposed** by this public `DocStoreClient`; package presence is not full
query-feature parity. See the [DocStore API reference](api/docstore.md).

## Shared client interfaces

All clients above expose `close` and context-manager cleanup. Client properties
such as provider, region, resource name, or the DocStore driver handle are
accessors rather than additional cloud operations. The [API reference](api/index.md)
contains complete signatures and the shared models and exception hierarchy.

## Remaining work

- Implement the planned Ali providers; placeholder distributions do not provide
  working operations.
- Extend public DocStore functionality and its integration coverage before
  documenting query/filter/pagination support as available.
- Keep this inventory and the service guides aligned with implemented behavior
  as source changes merge. New services and dates should be added only when
  there is an agreed plan; the previous July 2026 targets are not current status.
