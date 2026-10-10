# Critical workflows

| Workflow | Business risk | Release oracle |
|---|---|---|
| Login/logout | Users cannot reach or leave the product safely | Authenticated dashboard appears; logout removes access |
| Project persistence | Customer work disappears or is not saved | Created project remains after refresh |
| Subscription entitlement | Restricted features are granted incorrectly | Pro sees analytics; free plan sees unavailable state |
| Role permissions | Users perform actions outside their role | Viewer receives 403 on project creation |
| Webhook processing | Billing state is duplicated or corrupted | First event processes; duplicate is idempotent; unknown type is rejected |
