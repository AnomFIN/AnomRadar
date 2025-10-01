import axios from 'axios';
import * as cheerio from 'cheerio';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

export interface ContactResult {
  findings: Finding[];
}

/**
 * Contact Scraper
 * Extracts contact information from websites
 */
export class ContactScraper {
  private config: Config;
  private emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  private phoneRegex = /(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}/g;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<ContactResult> {
    logger.info(`Contact: Scraping ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Try common contact pages
      const pages = [
        '/',
        '/contact',
        '/contact-us',
        '/about',
        '/about-us',
        '/impressum',
      ];

      const emails = new Set<string>();
      const phones = new Set<string>();

      for (const page of pages) {
        try {
          const url = `https://${domain}${page}`;
          const response = await axios.get(url, {
            timeout: 10000,
            headers: {
              'User-Agent': 'AnomRadar/1.0 (Security Scanner)',
            },
            validateStatus: (status) => status < 500, // Accept 4xx responses
          });

          if (response.status === 200) {
            const $ = cheerio.load(response.data);
            const text = $('body').text();

            // Extract emails
            const foundEmails = text.match(this.emailRegex);
            if (foundEmails) {
              foundEmails.forEach(email => emails.add(email.toLowerCase()));
            }

            // Extract phone numbers
            const foundPhones = text.match(this.phoneRegex);
            if (foundPhones) {
              foundPhones.forEach(phone => phones.add(phone.trim()));
            }
          }
        } catch (e) {
          // Skip failed pages
        }
      }

      // Check for exposed emails
      if (emails.size > 0) {
        findings.push({
          type: 'contact_emails_found',
          severity: 'info',
          title: 'Contact Emails Found',
          description: `Found ${emails.size} email address(es) on the website`,
          recommendation: 'Consider using contact forms to reduce spam',
          evidence: {
            emails: Array.from(emails).slice(0, 5), // Limit to 5 for privacy
          },
        });

        // Check for admin/sensitive emails
        const sensitivePatterns = ['admin', 'root', 'webmaster', 'info', 'support'];
        emails.forEach(email => {
          if (sensitivePatterns.some(pattern => email.includes(pattern))) {
            findings.push({
              type: 'contact_sensitive_email',
              severity: 'low',
              title: 'Potentially Sensitive Email Exposed',
              description: `Email with common administrative pattern: ${email}`,
              recommendation: 'Consider using role-based email aliases',
              evidence: { email },
            });
          }
        });
      }

      if (phones.size > 0) {
        findings.push({
          type: 'contact_phones_found',
          severity: 'info',
          title: 'Contact Phone Numbers Found',
          description: `Found ${phones.size} phone number(s) on the website`,
          evidence: {
            phones: Array.from(phones).slice(0, 3),
          },
        });
      }

      logger.info(`Contact: Found ${emails.size} emails, ${phones.size} phones for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`Contact: Scraping failed for ${domain}:`, error);
      return { findings };
    }
  }

  private simulateScan(domain: string): ContactResult {
    logger.info('Contact: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'contact_simulation',
          severity: 'info',
          title: 'Contact Scraping Simulation',
          description: `Simulated contact scraping for ${domain}`,
        },
      ],
    };
  }
}
