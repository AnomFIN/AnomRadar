import axios from 'axios';
import * as cheerio from 'cheerio';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

export interface TechStackResult {
  findings: Finding[];
}

/**
 * Technology Stack Scanner
 * Detects technologies, frameworks, and CMS used by the website
 */
export class TechStackScanner {
  private config: Config;

  // Technology fingerprints
  private techPatterns = {
    // CMS
    'WordPress': [/wp-content/i, /wp-includes/i, /wordpress/i],
    'Drupal': [/drupal/i, /sites\/default/i],
    'Joomla': [/joomla/i, /com_content/i],
    'Magento': [/magento/i, /mage\/cookies/i],
    'Shopify': [/shopify/i, /cdn\.shopify/i],
    'Wix': [/wix\.com/i, /static\.parastorage/i],
    'Squarespace': [/squarespace/i],
    
    // Frameworks
    'React': [/react/i, /_next\/static/i, /react-dom/i],
    'Angular': [/angular/i, /ng-/i],
    'Vue.js': [/vue/i, /vuejs/i],
    'jQuery': [/jquery/i, /\$\(/],
    'Bootstrap': [/bootstrap/i],
    'Tailwind CSS': [/tailwind/i],
    
    // Web Servers
    'Apache': [/apache/i],
    'Nginx': [/nginx/i],
    'IIS': [/iis/i, /microsoft-iis/i],
    
    // Languages/Platforms
    'PHP': [/\.php/i, /phpsessid/i],
    'ASP.NET': [/\.aspx/i, /asp\.net/i, /viewstate/i],
    'Node.js': [/node/i, /express/i],
    'Ruby on Rails': [/rails/i, /ruby/i],
    'Django': [/django/i, /csrfmiddlewaretoken/i],
    
    // Analytics
    'Google Analytics': [/google-analytics/i, /gtag/i, /ga\.js/i],
    'Google Tag Manager': [/googletagmanager/i],
    'Hotjar': [/hotjar/i],
    'Matomo': [/matomo/i, /piwik/i],
    
    // CDN
    'Cloudflare': [/cloudflare/i, /cf-ray/i],
    'Amazon CloudFront': [/cloudfront/i],
    'Akamai': [/akamai/i],
  };

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<TechStackResult> {
    logger.info(`TechStack: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Fetch website and headers
      const response = await axios.get(`https://${domain}`, {
        timeout: 10000,
        headers: {
          'User-Agent': 'AnomRadar/1.0 (Security Scanner)',
        },
        maxRedirects: 5,
        validateStatus: (status) => status < 500,
      });

      const $ = cheerio.load(response.data);
      const headers = response.headers;
      const html = response.data;

      // Detect technologies
      const detectedTech = new Set<string>();

      // Check headers
      const serverHeader = headers['server'] || headers['Server'] || '';
      const poweredBy = headers['x-powered-by'] || headers['X-Powered-By'] || '';
      
      for (const [tech, patterns] of Object.entries(this.techPatterns)) {
        for (const pattern of patterns) {
          if (pattern.test(serverHeader) || pattern.test(poweredBy) || pattern.test(html)) {
            detectedTech.add(tech);
            break;
          }
        }
      }

      // Check for outdated technologies
      const outdatedTech = this.checkOutdatedTechnologies(detectedTech, html, headers);
      
      if (outdatedTech.length > 0) {
        findings.push({
          type: 'tech_outdated',
          severity: 'high',
          title: 'Outdated Technologies Detected',
          description: `Found potentially outdated: ${outdatedTech.join(', ')}`,
          recommendation: 'Update to latest stable versions to patch security vulnerabilities',
          evidence: { outdated: outdatedTech },
        });
      }

      // Report detected technologies
      if (detectedTech.size > 0) {
        findings.push({
          type: 'tech_stack_detected',
          severity: 'info',
          title: 'Technology Stack Detected',
          description: `Detected ${detectedTech.size} technolog(ies)`,
          evidence: { technologies: Array.from(detectedTech) },
        });

        // Check for vulnerable technologies
        const vulnerableTech = this.checkVulnerableTechnologies(Array.from(detectedTech));
        if (vulnerableTech.length > 0) {
          findings.push({
            type: 'tech_vulnerable',
            severity: 'high',
            title: 'Potentially Vulnerable Technologies',
            description: `Technologies with known vulnerabilities: ${vulnerableTech.join(', ')}`,
            recommendation: 'Update or patch these technologies immediately',
            evidence: { vulnerable: vulnerableTech },
          });
        }
      }

      // Check for technology version exposure
      const versionExposure = this.checkVersionExposure(html, headers);
      if (versionExposure.length > 0) {
        findings.push({
          type: 'tech_version_exposure',
          severity: 'medium',
          title: 'Technology Version Information Exposed',
          description: 'Specific version numbers are visible',
          recommendation: 'Hide version information to reduce attack surface',
          evidence: { exposed_versions: versionExposure },
        });
      }

      // Check for development/debug modes
      if (this.checkDebugMode(html, headers)) {
        findings.push({
          type: 'tech_debug_enabled',
          severity: 'critical',
          title: 'Debug/Development Mode Enabled',
          description: 'Website appears to be running in debug or development mode',
          recommendation: 'Disable debug mode in production immediately',
        });
      }

      // Check security headers
      const missingHeaders = this.checkSecurityHeaders(headers);
      if (missingHeaders.length > 0) {
        findings.push({
          type: 'tech_missing_security_headers',
          severity: 'medium',
          title: 'Missing Security Headers',
          description: `Missing: ${missingHeaders.join(', ')}`,
          recommendation: 'Implement recommended security headers',
          evidence: { missing_headers: missingHeaders },
        });
      }

      // Check for common vulnerabilities
      const commonVulns = this.checkCommonVulnerabilities($, html);
      findings.push(...commonVulns);

      logger.info(`TechStack: Found ${findings.length} items for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`TechStack: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private checkOutdatedTechnologies(detectedTech: Set<string>, html: string, headers: any): string[] {
    const outdated: string[] = [];

    // Check for specific outdated versions
    if (detectedTech.has('jQuery')) {
      const jqueryMatch = html.match(/jquery[/-](\d+\.\d+)/i);
      if (jqueryMatch) {
        const version = parseFloat(jqueryMatch[1]);
        if (version < 3.0) {
          outdated.push(`jQuery ${version}`);
        }
      }
    }

    if (detectedTech.has('PHP')) {
      const phpVersion = headers['x-powered-by'] || '';
      const phpMatch = phpVersion.match(/PHP\/(\d+\.\d+)/);
      if (phpMatch) {
        const version = parseFloat(phpMatch[1]);
        if (version < 7.4) {
          outdated.push(`PHP ${version}`);
        }
      }
    }

    return outdated;
  }

  private checkVulnerableTechnologies(technologies: string[]): string[] {
    const vulnerable: string[] = [];

    // Known vulnerable technologies (this would ideally be a database)
    const knownVulnerable = ['jQuery', 'WordPress', 'Drupal', 'Joomla'];

    for (const tech of technologies) {
      if (knownVulnerable.includes(tech)) {
        vulnerable.push(tech);
      }
    }

    return vulnerable;
  }

  private checkVersionExposure(html: string, headers: any): string[] {
    const exposed: string[] = [];

    // Check for version in headers
    const serverHeader = headers['server'] || '';
    const versionMatch = serverHeader.match(/\/(\d+\.\d+(\.\d+)?)/);
    if (versionMatch) {
      exposed.push(`Server: ${serverHeader}`);
    }

    // Check for generator meta tag
    const generatorMatch = html.match(/<meta name="generator" content="([^"]+)"/i);
    if (generatorMatch) {
      exposed.push(`Generator: ${generatorMatch[1]}`);
    }

    return exposed;
  }

  private checkDebugMode(html: string, headers: any): boolean {
    const debugPatterns = [
      /debug.*?true/i,
      /development mode/i,
      /stack trace/i,
      /error.*?line \d+/i,
      /warning.*?in.*?on line/i,
    ];

    return debugPatterns.some(pattern => pattern.test(html)) ||
           (headers['x-debug'] || '').toLowerCase() === 'true';
  }

  private checkSecurityHeaders(headers: any): string[] {
    const missing: string[] = [];
    const recommendedHeaders = [
      'Strict-Transport-Security',
      'X-Content-Type-Options',
      'X-Frame-Options',
      'Content-Security-Policy',
      'X-XSS-Protection',
      'Referrer-Policy',
    ];

    for (const header of recommendedHeaders) {
      const headerLower = header.toLowerCase();
      const found = Object.keys(headers).some(k => k.toLowerCase() === headerLower);
      if (!found) {
        missing.push(header);
      }
    }

    return missing;
  }

  private checkCommonVulnerabilities(_$: any, html: string): Finding[] {
    const findings: Finding[] = [];

    // Check for exposed admin panels
    const adminPaths = ['/admin', '/wp-admin', '/administrator', '/login'];
    // Note: We're not actually requesting these, just checking if they're linked
    adminPaths.forEach(path => {
      if (html.includes(`href="${path}`) || html.includes(`href='${path}`)) {
        findings.push({
          type: 'tech_admin_panel_exposed',
          severity: 'medium',
          title: 'Admin Panel Link Found',
          description: `Found link to admin panel: ${path}`,
          recommendation: 'Restrict admin panel access and use non-standard URLs',
          evidence: { path },
        });
      }
    });

    // Check for commented credentials
    const commentPattern = /<!--[\s\S]*?(password|username|apikey|secret|token)[\s\S]*?-->/gi;
    const matches = html.match(commentPattern);
    if (matches) {
      findings.push({
        type: 'tech_credentials_in_comments',
        severity: 'high',
        title: 'Potential Credentials in HTML Comments',
        description: 'Found sensitive keywords in HTML comments',
        recommendation: 'Remove all comments containing sensitive information',
      });
    }

    return findings;
  }

  private simulateScan(domain: string): TechStackResult {
    logger.info('TechStack: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'tech_simulation',
          severity: 'info',
          title: 'Technology Stack Simulation',
          description: `Simulated tech stack scan for ${domain}`,
        },
      ],
    };
  }
}
