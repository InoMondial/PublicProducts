# G20 integration profile — install/update/post-install stage

A separate G20 candidate owns the cross-host setup lifecycle. Version 3.0.4 makes the common private parameter catalog and conversational/CLI setup plan executable as a companion, but G20 is NOT silently promoted to a twentieth core governance member.

States: `UNINITIALIZED -> DRAFT -> AWAITING_AUTHORIZATION -> CONNECTOR_VERIFIED -> READY_FOR_DEPENDENT_ACTIONS`. Errors/expired permissions become `REVALIDATION_REQUIRED`.

The installer must perform deterministic parameter qualification, then delegate connection and identity verification to a trusted host connector. The package never asks for passwords, tokens or OAuth codes and it never self-claims successful third-party app authorization. Initial ChatGPT skill upload is not secondary setup.

Persist non-secret configuration by approved private provider; pin file SHA-256 where a local file actually exists, use GitHub private repository only for versioned *schema*, and bind private values to an approved store with project/account isolation. Simulated tests are evidence of algorithms, not proof of native ChatGPT/Work/O365 installation.
