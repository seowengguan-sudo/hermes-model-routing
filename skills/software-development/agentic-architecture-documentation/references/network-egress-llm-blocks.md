# Network Egress Blocks for LLM Providers (Sandbox Environment)

This document details specific network egress issues observed when attempting direct API calls to various LLM providers from the Hermes Agent sandbox environment (WSL2 Docker container).

## Observed Blocks

*   **Groq & Cerebras (Cloudflare Error 1010 - ASN Ban)**
    *   **Symptom:** HTTP 403 Forbidden with Cloudflare error code 1010 in the response body.
    *   **Root Cause:** Cloudflare Web Application Firewall (WAF) is blocking the entire Autonomous System Number (ASN) of the egress IP. The egress IP `161.142.137.99` (TTNET, George Town, Penang, Malaysia) is identified as the source of the block.
    *   **Impact:** Direct API calls to these providers are completely blocked, regardless of API key validity or request formatting.
    *   **Solution:** Requires routing through an egress point with a different ASN (e.g., VPN, proxy) or utilizing Hermes's native gateway integration if available and unblocked.

*   **HuggingFace (DNS Resolution Failure)**
    *   **Symptom:** `Name or service not known` error during DNS resolution for `api-inference.huggingface.co`.
    *   **Root Cause:** The specific subdomain `api-inference.huggingface.co` is not present in the sandbox environment's DNS allowlist or faces a specific network policy restriction.
    *   **Impact:** No direct API inference calls can be made to HuggingFace models via this endpoint.
    *   **Solution:** Requires modification of the sandbox's DNS allowlist/network policy or routing through an external service that can resolve the domain.

*   **Nous Portal (Vercel Security Checkpoint / Rate Limit)**
    *   **Symptom:** HTTP 429 Too Many Requests, returning a Vercel Security Checkpoint HTML page.
    *   **Root Cause:** Direct API calls to `portal.nousresearch.com` are subject to strict rate limits or Vercel's security measures, which differentiate from its OAuth/gateway integration.
    *   **Impact:** Direct API calls are throttled or temporarily blocked.
    *   **Solution:** Utilize Hermes's native OAuth/gateway integration for Nous Portal, which bypasses these direct API restrictions.

## Egress IP & Network Context

*   **Outbound IP:** `161.142.137.99`
*   **ASN/Organization:** AS9930 TTNET
*   **Geolocation:** George Town, Penang, Malaysia
*   **Note:** The egress IP from the Docker (WSL2) container is identical to the Windows host's public IP. Removing Docker would not change these egress-related blockages; the issue is with the network's ASN reputation or DNS policies.
