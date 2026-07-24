# OWASP MASVS 2.1.0 — throughline source

This document is **generated from the graph** by `tl docs`; `tl docs --check` gates
it in CI. The prose headings are hand-owned — everything between `tl:*` markers is
injected from the YAML items, so the published spec can never drift from the graph.

This source is a faithful, complete cut of **OWASP MASVS v2.1.0**: every category is
a `user_requirement`, and every control is a `system_requirement` that `implements` its
category. The published MASVS id lives in `attrs.source_ref` (e.g. `MASVS-STORAGE-1`). The
throughline UIDs are this source's own and immutable — a consumer cites a control as
`masvs:SR-0001`, never by its MASVS id.

It carries
<!-- tl:count type == 'user_requirement' -->
8
<!-- tl:end --> categories and
<!-- tl:count type == 'system_requirement' -->
24
<!-- tl:end --> controls.

## Purpose

<!-- tl:item INT-0001 -->
**INT-0001 — A mobile application's security is verifiable against a consistent baseline** — `intent`, status `approved`

> The OWASP Mobile Application Security Verification Standard exists so that a mobile app's security controls can be verified against a normative, consistent baseline — giving mobile architects, developers and testers a shared reference for what a secure mobile app must do, rather than ad-hoc judgement.

**source_ref**: MASVS 2.1.0
<!-- tl:end -->

## MASVS-STORAGE Storage

<!-- tl:item UR-0001 -->
**UR-0001 — MASVS-STORAGE Storage** — `user_requirement`, status `approved`

> Mobile applications handle a wide variety of sensitive data, such as personally identifiable information (PII), cryptographic material, secrets, and API keys, that often need to be stored locally. This sensitive data may be stored in private locations, such as the app's internal storage, or in public folders that are accessible by the user or other apps installed on the device. However, sensitive data can also be unintentionally stored or exposed to publicly accessible locations, typically as a side-effect of using certain APIs or system capabilities such as backups or logs. This category is designed to help developers ensure that any sensitive data intentionally stored by the app is properly protected, regardless of the target location. It also covers unintentional leaks that can occur due to improper use of APIs or system capabilities.

*Derives from:* INT-0001

**source_ref**: MASVS-STORAGE
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-STORAGE-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0001 | system_requirement | approved | Securely stores sensitive data |
| SR-0002 | system_requirement | approved | Prevents leakage of sensitive data |
<!-- tl:end -->

## MASVS-CRYPTO Cryptography

<!-- tl:item UR-0002 -->
**UR-0002 — MASVS-CRYPTO Cryptography** — `user_requirement`, status `approved`

> Cryptography is essential for mobile apps because mobile devices are highly portable and can be easily lost or stolen. This means that an attacker who gains physical access to a device can potentially access all the sensitive data stored on it, including passwords, financial information, and personally identifiable information. Cryptography provides a means of protecting this sensitive data by encrypting it so that it cannot be easily read or accessed by an unauthorized user. The purpose of the controls in this category is to ensure that the verified app uses cryptography according to industry best practices, which are typically defined in external standards such as NIST.SP.800-175B and NIST.SP.800-57. This category also focuses on the management of cryptographic keys throughout their lifecycle, including key generation, storage, and protection. Poor key management can compromise even the strongest cryptography, so it is crucial for developers to follow the recommended best practices to ensure the security of their users' sensitive data.

*Derives from:* INT-0001

**source_ref**: MASVS-CRYPTO
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-CRYPTO-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0003 | system_requirement | approved | Employs current strong cryptography and uses it according to industry best practices |
| SR-0004 | system_requirement | approved | Performs key management according to industry best practices |
<!-- tl:end -->

## MASVS-AUTH Authentication and Authorization

<!-- tl:item UR-0003 -->
**UR-0003 — MASVS-AUTH Authentication and Authorization** — `user_requirement`, status `approved`

> Authentication and authorization are essential components of most mobile apps, especially those that connect to a remote service. These mechanisms provide an added layer of security and help prevent unauthorized access to sensitive user data. Although the enforcement of these mechanisms must be on the remote endpoint, it is equally important for the app to follow relevant best practices to ensure the secure use of the involved protocols. Mobile apps often use different forms of authentication, such as biometrics, PIN, or multi-factor authentication code generators, to validate user identity. These mechanisms must be implemented correctly to ensure their effectiveness in preventing unauthorized access. Additionally, some apps may rely solely on local app authentication and may not have a remote endpoint. In such cases, it is critical to ensure that local authentication mechanisms are secure and implemented following industry best practices. The controls in this category aim to ensure that the app implements authentication and authorization mechanisms securely, protecting sensitive user information and preventing unauthorized access. It is important to note that the security of the remote endpoint should also be validated using industry standards such as the OWASP Application Security Verification Standard (ASVS).

*Derives from:* INT-0001

**source_ref**: MASVS-AUTH
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-AUTH-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0005 | system_requirement | approved | Uses secure authentication and authorization protocols and follows the relevant best practices |
| SR-0006 | system_requirement | approved | Performs local authentication securely according to the platform best practices |
| SR-0007 | system_requirement | approved | Secures sensitive operations with additional authentication |
<!-- tl:end -->

## MASVS-NETWORK Network Communication

<!-- tl:item UR-0004 -->
**UR-0004 — MASVS-NETWORK Network Communication** — `user_requirement`, status `approved`

> Secure networking is a critical aspect of mobile app security, particularly for apps that communicate over the network. In order to ensure the confidentiality and integrity of data in transit, developers typically rely on encryption and authentication of the remote endpoint, such as through the use of TLS. However, there are numerous ways in which a developer may accidentally disable the platform secure defaults or bypass them entirely by utilizing low-level APIs or third-party libraries. This category is designed to ensure that the mobile app sets up secure connections under any circumstances. Specifically, it focuses on verifying that the app establishes a secure, encrypted channel for network communication. Additionally, this category covers situations where a developer may choose to trust only specific Certificate Authorities (CAs), which is commonly referred to as certificate pinning or public key pinning.

*Derives from:* INT-0001

**source_ref**: MASVS-NETWORK
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-NETWORK-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0008 | system_requirement | approved | Secures all network traffic according to the current best practices |
| SR-0009 | system_requirement | approved | Performs identity pinning for all remote endpoints under the developer's control |
<!-- tl:end -->

## MASVS-PLATFORM Platform Interaction

<!-- tl:item UR-0005 -->
**UR-0005 — MASVS-PLATFORM Platform Interaction** — `user_requirement`, status `approved`

> The security of mobile apps heavily depends on their interaction with the mobile platform, which often involves exposing data or functionality intentionally through the use of platform-provided inter-process communication (IPC) mechanisms and WebViews to enhance the user experience. However, these mechanisms can also be exploited by attackers or other installed apps, potentially compromising the app's security. Furthermore, sensitive data, such as passwords, credit card details, and one-time passwords in notifications, is often displayed in the app's user interface. It is essential to ensure that this data is not unintentionally leaked through platform mechanisms such as auto-generated screenshots or accidental disclosure through shoulder surfing or device sharing. This category comprises controls that ensure the app's interactions with the mobile platform occur securely. These controls cover the secure use of platform-provided IPC mechanisms, WebView configurations to prevent sensitive data leakage and functionality exposure, and secure display of sensitive data in the app's user interface. By implementing these controls, mobile app developers can safeguard sensitive user information and prevent unauthorized access by attackers.

*Derives from:* INT-0001

**source_ref**: MASVS-PLATFORM
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-PLATFORM-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0010 | system_requirement | approved | Uses IPC mechanisms securely |
| SR-0011 | system_requirement | approved | Uses WebViews securely |
| SR-0012 | system_requirement | approved | Uses the user interface securely |
<!-- tl:end -->

## MASVS-CODE Code Quality

<!-- tl:item UR-0006 -->
**UR-0006 — MASVS-CODE Code Quality** — `user_requirement`, status `approved`

> Mobile apps have many data entry points, including the UI, IPC, network, and file system, which might receive data that has been inadvertently modified by untrusted actors. By treating this data as untrusted input and properly verifying and sanitizing it before use, developers can prevent classical injection attacks, such as SQL injection, XSS, or insecure deserialization. However, other common coding vulnerabilities, such as memory corruption flaws, are hard to detect in penetration testing but easy to prevent with secure architecture and coding practices. Developers should follow best practices such as the OWASP Software Assurance Maturity Model (SAMM) and NIST.SP.800-218 Secure Software Development Framework (SSDF) to avoid introducing these flaws in the first place. This category covers coding vulnerabilities that arise from external sources such as app data entry points, the OS, and third-party software components. Developers should verify and sanitize all incoming data to prevent injection attacks and bypass of security checks. They should also enforce app updates and ensure that the app runs up-to-date platforms to protect users from known vulnerabilities.

*Derives from:* INT-0001

**source_ref**: MASVS-CODE
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-CODE-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0013 | system_requirement | approved | Requires an up-to-date platform version |
| SR-0014 | system_requirement | approved | Has a mechanism for enforcing app updates |
| SR-0015 | system_requirement | approved | Only uses software components without known vulnerabilities |
| SR-0016 | system_requirement | approved | Validates and sanitizes all untrusted inputs |
<!-- tl:end -->

## MASVS-RESILIENCE Resilience Against Reverse Engineering and Tampering

<!-- tl:item UR-0007 -->
**UR-0007 — MASVS-RESILIENCE Resilience Against Reverse Engineering and Tampering** — `user_requirement`, status `approved`

> Defense-in-depth measures such as code obfuscation, anti-debugging, anti-tampering, etc. are important to increase app resilience against reverse engineering and specific client-side attacks. They add multiple layers of security controls to the app, making it more difficult for attackers to successfully reverse engineer and extract valuable intellectual property or sensitive data from it, which could result in: - The theft or compromise of valuable business assets such as proprietary algorithms, trade secrets, or customer data - Significant financial losses due to loss of revenue or legal action - Legal and reputational damage due to breach of contracts or regulations - Damage to brand reputation due to negative publicity or customer dissatisfaction The controls in this category aim to ensure that the app is running on a trusted platform, prevent tampering at runtime and ensure the integrity of the app's intended functionality. Additionally, the controls impede comprehension by making it difficult to figure out how the app works using static analysis and prevent dynamic analysis and instrumentation that could allow an attacker to modify the code at runtime. However, note that the lack of any of these measures does not necessarily cause vulnerabilities - instead, they add threat-specific additional protection to apps which must also fulfil the rest of the OWASP MASVS security controls according to their specific threat models.

*Derives from:* INT-0001

**source_ref**: MASVS-RESILIENCE
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-RESILIENCE-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0017 | system_requirement | approved | Validates the integrity of the platform |
| SR-0018 | system_requirement | approved | Implements anti-tampering mechanisms |
| SR-0019 | system_requirement | approved | Implements anti-static analysis mechanisms |
| SR-0020 | system_requirement | approved | Implements anti-dynamic analysis techniques |
<!-- tl:end -->

## MASVS-PRIVACY Privacy

<!-- tl:item UR-0008 -->
**UR-0008 — MASVS-PRIVACY Privacy** — `user_requirement`, status `approved`

> The main goal of MASVS-PRIVACY is to provide a **baseline for user privacy**. It is not intended to cover all aspects of user privacy, especially when other standards and regulations such as ENISA or the GDPR already do that. We focus on the app itself, looking at what can be tested using information that's publicly available or found within the app through methods like static or dynamic analysis. While some associated tests can be automated, others necessitate manual intervention due to the nuanced nature of privacy. For example, if an app collects data that it didn't mention in the app store or its privacy policy, it takes careful manual checking to spot this. > **Note on "Data Collection and Sharing"**:For the MASTG tests, we treat "Collect" and "Share" in a unified manner. This means that whether the app is sending data to another server or transferring it to another app on the device, we view it as data that's potentially leaving the user's control. Validating what happens to the data on remote endpoints is challenging and often not feasible due to access restrictions and the dynamic nature of server-side operations. Therefore, this issue is outside of the scope of the MASVS. **IMPORTANT DISCLAIMER**: MASVS-PRIVACY is not intended to serve as an exhaustive or exclusive reference. While it provides valuable guidance on app-centric privacy considerations, it should never replace comprehensive assessments, such as a Data Protection Impact Assessment (DPIA) mandated by the General Data Protection Regulation (GDPR) or other pertinent legal and regulatory frameworks. Stakeholders are strongly advised to undertake a holistic approach to privacy, integrating MASVS-PRIVACY insights with broader assessments to ensure comprehensive data protection compliance. Given the specialized nature of privacy regulations and the complexity of data protection, these assessments are best conducted by privacy experts rather than security experts.

*Derives from:* INT-0001

**source_ref**: MASVS-PRIVACY
<!-- tl:end -->

<!-- tl:table type == 'system_requirement' and attrs.get('source_ref').startswith('MASVS-PRIVACY-') -->
| UID | Type | Status | Title |
|---|---|---|---|
| SR-0021 | system_requirement | approved | Minimizes access to sensitive data and resources |
| SR-0022 | system_requirement | approved | Prevents identification of the user |
| SR-0023 | system_requirement | approved | Is transparent about data collection and usage |
| SR-0024 | system_requirement | approved | Offers user control over their data |
<!-- tl:end -->

