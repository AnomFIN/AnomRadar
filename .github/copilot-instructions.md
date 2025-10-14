# GitHub Copilot Instructions for AnomRadar

## Project Overview

AnomRadar is a comprehensive OSINT (Open Source Intelligence) security scanning and reporting system designed to identify and report company security flaws. The system performs **passive reconnaissance only** - no active attacks or intrusive testing.

### Architecture

The project is a monorepo with three main components:

1. **Backend Scanner** (`backend/`) - Node.js + TypeScript scanner with 12 OSINT modules
2. **REST API** (`api/`) - PHP 8.1+ REST API with MySQL 8.0 database
3. **Frontend** (`frontend/`) - Static HTML/CSS/JavaScript interface

## Code Style and Standards

### TypeScript/Node.js (Backend)

- **TypeScript Version**: 5.2.2 with strict mode enabled
- **Target**: ES2020, CommonJS modules
- **Style**:
  - Use explicit type annotations for function parameters and return types
  - Prefer `const` over `let`, never use `var`
  - Use async/await instead of promises with `.then()`
  - Add JSDoc comments for all public classes and methods
  - Use single quotes for strings
  - End statements with semicolons
  - Use 2 spaces for indentation
  
- **Imports**:
  - Group imports: external libraries first, then internal modules
  - Use destructuring for imports when appropriate
  
- **Error Handling**:
  - Always use try-catch blocks for async operations
  - Log errors using the `logger` utility, never `console.log`
  - Throw typed errors with meaningful messages

- **Example**:
  ```typescript
  import { logger } from '../utils/logger';
  
  /**
   * Scanner for DNS analysis
   */
  export class DnsScanner {
    async scan(domain: string): Promise<DnsResult> {
      logger.info(`DNS: Scanning ${domain}`);
      try {
        // Implementation
      } catch (error) {
        logger.error('DNS scan failed', { domain, error });
        throw error;
      }
    }
  }
  ```

### PHP (API)

- **PHP Version**: 8.1+
- **Style**:
  - Always use `declare(strict_types=1);` at the top of each file
  - Use type hints for all parameters and return types
  - Follow PSR-12 coding standard
  - Use 4 spaces for indentation
  - Use namespaces: `AnomRadar\Api\{Component}`
  - Use meaningful variable names in camelCase
  
- **Classes**:
  - One class per file
  - Add docblocks for all public methods
  - Use dependency injection where appropriate
  
- **Database**:
  - Always use prepared statements (PDO)
  - Never concatenate SQL strings
  - Use the Database singleton: `Database::getInstance()`

- **Example**:
  ```php
  <?php
  
  declare(strict_types=1);
  
  namespace AnomRadar\Api\Controllers;
  
  /**
   * Scan controller
   */
  class ScanController
  {
      public function getScan(int $id): array
      {
          // Implementation
      }
  }
  ```

### Frontend (HTML/CSS/JavaScript)

- **JavaScript**:
  - Use ES6+ features
  - Use `const` and `let`, never `var`
  - Use async/await for API calls with Fetch API
  - Add error handling for all API requests
  - Use descriptive function and variable names
  
- **CSS**:
  - Use consistent naming conventions
  - Prefer classes over IDs for styling
  - Mobile-first responsive design
  
- **HTML**:
  - Use semantic HTML5 elements
  - Add ARIA labels for accessibility

## Security Guidelines

### Critical Security Rules

1. **Never commit secrets or credentials**:
   - Use `.env` files for all sensitive data
   - Never hardcode API keys, passwords, or tokens
   - Check `.env` is in `.gitignore`

2. **Passive scanning only**:
   - No active vulnerability exploitation
   - No penetration testing
   - No brute force attacks
   - Only passive information gathering

3. **Input validation**:
   - Validate all user input
   - Sanitize domain names and company names
   - Use parameterized queries for database operations
   - Escape output in HTML

4. **API security**:
   - Validate API keys where required
   - Use CORS appropriately
   - Rate limit API endpoints
   - Return appropriate HTTP status codes

5. **Data protection**:
   - Store passwords hashed (never plaintext)
   - Use HTTPS in production
   - Implement 90-day data retention policy
   - Log security events

### Environment Variables

- **Backend** uses `backend/.env` for configuration
- **API** uses `api/.env` for configuration
- Always provide `.env.example` files with placeholder values
- Document all environment variables in README.md

## Testing

### Backend (TypeScript)

- Use Jest for unit tests
- Test files: `*.test.ts` alongside source files
- Run tests: `npm test`
- Target: 80%+ code coverage for critical modules
- Mock external services (YTJ API, ZAP, nmap)

### API (PHP)

- Use PHPUnit for unit tests
- Test files in `tests/` directory
- Run tests: `composer test`
- Test all controllers and database operations
- Mock database connections in tests

### Frontend

- Manual testing in browser
- Test across Chrome, Firefox, Safari
- Test responsive design on mobile devices
- Verify all API integrations work

## Configuration Management

### Environment Files

- Never commit `.env` files
- Always update `.env.example` when adding new variables
- Document default values and valid options
- Use sensible defaults where possible

### Simulation Mode

- `SIMULATION_MODE=false` by default (real scans)
- When true, return mock data instead of real scans
- Useful for testing without external dependencies

## Dependencies

### Version Pinning

- All dependencies use **exact versions** for reproducibility
- Update dependencies carefully and test thoroughly
- Document breaking changes in commit messages

### Backend Dependencies

- axios: 1.6.0 - HTTP client
- cheerio: 1.0.0-rc.12 - HTML parsing
- dotenv: 16.3.1 - Environment variables
- mysql2: 3.6.3 - MySQL driver
- winston: 3.11.0 - Logging
- typescript: 5.2.2 - TypeScript compiler

### API Dependencies

- vlucas/phpdotenv: 5.5.0 - Environment variables
- tecnickcom/tcpdf: 6.6.5 - PDF generation

### Adding New Dependencies

- Only add dependencies when necessary
- Prefer well-maintained, popular libraries
- Check security advisories before adding
- Pin exact versions in `package.json` or `composer.json`

## Logging

### Backend Logging

- Use `logger` from `utils/logger.ts`
- Never use `console.log` in production code
- Log levels: error, warn, info, debug
- Include context in log messages

```typescript
import { logger } from './utils/logger';

logger.info('Starting scan', { domain, scanId });
logger.error('Scan failed', { domain, error: error.message });
```

### API Logging

- Log all API requests and errors
- Use appropriate log levels
- Include timestamps and request IDs

## Documentation

### Code Documentation

- Add JSDoc/PHPDoc comments for all public APIs
- Document parameters, return types, and exceptions
- Include usage examples for complex functions
- Keep documentation up-to-date with code changes

### Project Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for architectural changes
- Update installer/README.md for installation changes
- Keep PROJECT_PLAN.md as reference (don't modify)

### Comment Guidelines

- Write self-documenting code with clear names
- Add comments for complex logic or non-obvious decisions
- Avoid redundant comments that just restate the code
- Use TODO comments for planned improvements

## Database

### Schema

- Database: MySQL 8.0
- Character set: utf8mb4_unicode_ci
- Tables: scans, domains, findings, reports, whitelist, notifications, audit_log

### Migrations

- SQL migrations in `api/migrations/`
- Numbered sequentially: `001_initial_schema.sql`, `002_add_feature.sql`
- Include both up and down migrations when possible
- Test migrations on a copy of production data

### Queries

- Use prepared statements always
- Index frequently queried columns
- Optimize slow queries
- Use transactions for multi-step operations

## Risk Scoring

The system uses algorithmic risk scoring (0-100 scale):

- **0-30**: Low risk
- **31-60**: Medium risk  
- **61-100**: High risk

Weights:
- DMARC missing: +25
- SPF missing: +10
- Open admin ports: +20 max
- Web vulnerabilities: High +5, Medium +2
- HIBP breaches: +10

## Reports

### Report Generation

- Support HTML and PDF formats
- Use TCPDF library for PDF generation
- Store generated reports in `api/reports/generated/`
- Implement automatic cleanup (90-day retention)

## Notification System

### Whitelist-Only Notifications

- Notifications only sent to whitelisted contacts
- Support Telegram and WhatsApp
- Store whitelist in database
- Respect user privacy - no spam

## Common Patterns

### Scanning Pattern

All scanners follow this pattern:

```typescript
export class Scanner {
  async scan(target: string): Promise<ScanResult> {
    logger.info(`Scanner: Starting scan of ${target}`);
    
    if (this.config.simulationMode) {
      return this.simulateScan(target);
    }
    
    try {
      // Real scan logic
      const result = await this.performScan(target);
      logger.info(`Scanner: Completed scan of ${target}`);
      return result;
    } catch (error) {
      logger.error(`Scanner: Failed to scan ${target}`, { error });
      throw error;
    }
  }
  
  private simulateScan(target: string): ScanResult {
    // Return mock data for testing
  }
}
```

### API Response Pattern

All API endpoints use consistent response format:

```php
// Success
Response::success(['data' => $result], 200);

// Error
Response::error('Error message', 400);
```

## Build and Deployment

### Backend Build

```bash
cd backend
npm ci --production
npm run build
npm start
```

### API Setup

```bash
cd api
composer install --no-dev --optimize-autoloader
```

### Production Considerations

- Set `APP_ENV=production` in API
- Set `SIMULATION_MODE=false` in backend
- Use strong database passwords
- Enable HTTPS
- Configure web server (Apache/Nginx)
- Set up systemd services for backend

## File Organization

### Backend Structure

```
backend/
├── src/
│   ├── config/       # Configuration management
│   ├── scanners/     # Scanner modules
│   ├── risk-scoring/ # Risk calculation
│   └── utils/        # Utilities (logger, etc.)
└── dist/             # Compiled output
```

### API Structure

```
api/
├── src/
│   ├── Controllers/  # API controllers
│   ├── Database/     # Database connection
│   ├── Reports/      # Report generators
│   └── Utils/        # Utilities
├── public/           # Web-accessible files
└── migrations/       # Database migrations
```

## Additional Guidelines

### Performance

- Cache external API responses when appropriate
- Use connection pooling for database
- Implement request rate limiting
- Set appropriate timeouts (default: 5 minutes)

### Monitoring

- Log all errors and warnings
- Track scan completion times
- Monitor database size and performance
- Alert on failed scans

### Maintenance

- Review and update dependencies quarterly
- Clean up old scan data (90-day retention)
- Archive old reports
- Monitor disk space usage

## When Working on Issues

1. Read the issue description carefully
2. Review related documentation
3. Check existing code patterns
4. Write tests before implementing features
5. Follow the coding style guidelines
6. Update documentation if needed
7. Test thoroughly before committing
8. Write clear commit messages

## Questions?

- See README.md for general information
- See ARCHITECTURE.md for system design
- See installer/README.md for installation details
- See HOWTO.md for step-by-step setup guide
