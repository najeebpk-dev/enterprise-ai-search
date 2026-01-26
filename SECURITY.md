# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please report it through GitHub's Security Advisory feature or contact the maintainer through GitHub. All security vulnerabilities will be promptly addressed.

Please include the following information in your report:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability

## Security Best Practices

When using this project:

### 1. Credential Management
- **NEVER** commit `.env` files or credentials to version control
- Use Azure Key Vault or similar services for production credentials
- Rotate API keys regularly
- Use managed identities when deploying to Azure

### 2. Network Security
- Restrict Azure Search and OpenAI endpoints to specific IP ranges in production
- Enable Azure Private Link for private connectivity
- Use VNets for network isolation

### 3. Access Control
- Use Azure RBAC for fine-grained access control
- Implement least-privilege principle for service principals
- Enable Azure AD authentication where possible

### 4. Data Protection
- Encrypt data at rest (enabled by default in Azure)
- Use TLS 1.2+ for data in transit
- Implement data retention policies
- Be mindful of sensitive information in documents

### 5. Dependency Management
- Regularly update dependencies with `pip install --upgrade`
- Monitor security advisories for Azure SDKs
- Use tools like `safety` to check for vulnerable packages:
  ```bash
  pip install safety
  safety check -r requirements.txt
  ```

### 6. Logging and Monitoring
- Enable diagnostic logging for Azure resources
- Monitor for unusual API usage patterns
- Set up alerts for failed authentication attempts
- Avoid logging sensitive data

### 7. Input Validation
- The system sanitizes filenames for document IDs
- Be cautious with user-provided queries in production
- Implement rate limiting for API endpoints

## Known Security Considerations

1. **API Keys in Environment Variables**: This project uses environment variables for API keys, which is suitable for development but should be replaced with Azure Key Vault in production.

2. **Document Content**: Documents are indexed and searchable. Ensure you have appropriate permissions for all indexed content.

3. **OpenAI Data Processing**: Data sent to Azure OpenAI is processed according to Microsoft's data processing terms. Review Azure OpenAI's data handling policies.

## Disclosure Policy

- Security issues are taken seriously
- Vulnerabilities will be addressed promptly
- Credit will be given to reporters (unless anonymity is requested)
- Timeline for fixes depends on severity

## Contact

For security concerns: Use GitHub Security Advisories or contact maintainer via GitHub

For general issues: https://github.com/najeebpk-dev/enterprise-ai-search/issues
