import { exec } from 'child_process';
import { promisify } from 'util';
import axios from 'axios';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

const execAsync = promisify(exec);

export interface WHOISResult {
  findings: Finding[];
}

/**
 * WHOIS Scanner
 * Retrieves and analyzes domain registration information
 */
export class WHOISScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<WHOISResult> {
    logger.info(`WHOIS: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Get WHOIS data
      const whoisData = await this.getWHOISData(domain);

      if (!whoisData) {
        findings.push({
          type: 'whois_no_data',
          severity: 'low',
          title: 'WHOIS Data Not Available',
          description: `Could not retrieve WHOIS data for ${domain}`,
          recommendation: 'Verify domain is registered and accessible',
        });
        return { findings };
      }

      // Check domain expiration
      const expirationDate = this.extractExpirationDate(whoisData);
      if (expirationDate) {
        const daysUntilExpiry = Math.floor(
          (expirationDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
        );

        if (daysUntilExpiry < 0) {
          findings.push({
            type: 'whois_domain_expired',
            severity: 'critical',
            title: 'Domain Expired',
            description: `Domain expired ${Math.abs(daysUntilExpiry)} days ago`,
            recommendation: 'Renew domain immediately to prevent loss',
            evidence: { expiration_date: expirationDate.toISOString() },
          });
        } else if (daysUntilExpiry < 30) {
          findings.push({
            type: 'whois_domain_expiring_soon',
            severity: 'high',
            title: 'Domain Expiring Soon',
            description: `Domain expires in ${daysUntilExpiry} days`,
            recommendation: 'Renew domain as soon as possible',
            evidence: { expiration_date: expirationDate.toISOString(), days_remaining: daysUntilExpiry },
          });
        } else if (daysUntilExpiry < 90) {
          findings.push({
            type: 'whois_domain_expiring',
            severity: 'medium',
            title: 'Domain Expiring',
            description: `Domain expires in ${daysUntilExpiry} days`,
            recommendation: 'Plan to renew the domain',
            evidence: { expiration_date: expirationDate.toISOString(), days_remaining: daysUntilExpiry },
          });
        }
      }

      // Check for privacy protection
      const hasPrivacy = this.checkPrivacyProtection(whoisData);
      if (!hasPrivacy) {
        findings.push({
          type: 'whois_no_privacy',
          severity: 'low',
          title: 'No WHOIS Privacy Protection',
          description: 'Domain registrant information is publicly visible',
          recommendation: 'Consider enabling WHOIS privacy protection to hide personal information',
        });
      }

      // Check registrar
      const registrar = this.extractRegistrar(whoisData);
      if (registrar) {
        findings.push({
          type: 'whois_registrar_info',
          severity: 'info',
          title: 'Domain Registrar',
          description: `Domain registered with: ${registrar}`,
          evidence: { registrar },
        });
      }

      // Check nameservers
      const nameservers = this.extractNameservers(whoisData);
      if (nameservers.length === 0) {
        findings.push({
          type: 'whois_no_nameservers',
          severity: 'high',
          title: 'No Nameservers Found',
          description: 'Domain has no nameservers configured',
          recommendation: 'Configure nameservers for the domain',
        });
      } else {
        findings.push({
          type: 'whois_nameservers',
          severity: 'info',
          title: 'Nameservers Configured',
          description: `Found ${nameservers.length} nameserver(s)`,
          evidence: { nameservers },
        });
      }

      // Check creation date
      const creationDate = this.extractCreationDate(whoisData);
      if (creationDate) {
        const domainAge = Math.floor((Date.now() - creationDate.getTime()) / (1000 * 60 * 60 * 24));
        
        if (domainAge < 30) {
          findings.push({
            type: 'whois_new_domain',
            severity: 'medium',
            title: 'Recently Registered Domain',
            description: `Domain registered only ${domainAge} days ago`,
            recommendation: 'New domains may indicate higher risk; verify legitimacy',
            evidence: { creation_date: creationDate.toISOString(), age_days: domainAge },
          });
        }
      }

      // Check for domain lock status
      const isLocked = this.checkDomainLock(whoisData);
      if (!isLocked) {
        findings.push({
          type: 'whois_not_locked',
          severity: 'medium',
          title: 'Domain Not Locked',
          description: 'Domain transfer lock is not enabled',
          recommendation: 'Enable domain lock to prevent unauthorized transfers',
        });
      }

      logger.info(`WHOIS: Found ${findings.length} items for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`WHOIS: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private async getWHOISData(domain: string): Promise<string | null> {
    try {
      // Try using whois command
      const { stdout } = await execAsync(`whois ${domain}`, { timeout: 10000 });
      return stdout;
    } catch (error) {
      logger.warn(`WHOIS: Command failed for ${domain}, trying API`);
      
      // Fallback to WHOIS API (if available)
      try {
        const response = await axios.get(`https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey=at_free&domainName=${domain}`, {
          timeout: 10000,
        });
        return JSON.stringify(response.data);
      } catch (apiError) {
        return null;
      }
    }
  }

  private extractExpirationDate(whoisData: string): Date | null {
    const patterns = [
      /Registry Expiry Date:\s*(\d{4}-\d{2}-\d{2})/i,
      /Expiration Date:\s*(\d{4}-\d{2}-\d{2})/i,
      /Expiry.*?:\s*(\d{4}-\d{2}-\d{2})/i,
      /paid-till:\s*(\d{4}-\d{2}-\d{2})/i,
    ];

    for (const pattern of patterns) {
      const match = whoisData.match(pattern);
      if (match) {
        return new Date(match[1]);
      }
    }
    return null;
  }

  private extractCreationDate(whoisData: string): Date | null {
    const patterns = [
      /Creation Date:\s*(\d{4}-\d{2}-\d{2})/i,
      /Created.*?:\s*(\d{4}-\d{2}-\d{2})/i,
      /created:\s*(\d{4}-\d{2}-\d{2})/i,
    ];

    for (const pattern of patterns) {
      const match = whoisData.match(pattern);
      if (match) {
        return new Date(match[1]);
      }
    }
    return null;
  }

  private checkPrivacyProtection(whoisData: string): boolean {
    const privacyKeywords = ['privacy', 'private', 'redacted', 'protected', 'proxy'];
    const lowerData = whoisData.toLowerCase();
    return privacyKeywords.some(keyword => lowerData.includes(keyword));
  }

  private extractRegistrar(whoisData: string): string | null {
    const patterns = [
      /Registrar:\s*(.+)/i,
      /Sponsoring Registrar:\s*(.+)/i,
    ];

    for (const pattern of patterns) {
      const match = whoisData.match(pattern);
      if (match) {
        return match[1].trim();
      }
    }
    return null;
  }

  private extractNameservers(whoisData: string): string[] {
    const nameservers: string[] = [];
    const lines = whoisData.split('\n');

    for (const line of lines) {
      if (/name server/i.test(line) || /nserver/i.test(line)) {
        const parts = line.split(':');
        if (parts.length > 1) {
          const ns = parts[1].trim().split(/\s+/)[0];
          if (ns && !nameservers.includes(ns)) {
            nameservers.push(ns);
          }
        }
      }
    }

    return nameservers;
  }

  private checkDomainLock(whoisData: string): boolean {
    const lockKeywords = ['clientTransferProhibited', 'locked', 'serverTransferProhibited'];
    return lockKeywords.some(keyword => whoisData.includes(keyword));
  }

  private simulateScan(domain: string): WHOISResult {
    logger.info('WHOIS: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'whois_simulation',
          severity: 'info',
          title: 'WHOIS Simulation',
          description: `Simulated WHOIS scan for ${domain}`,
        },
      ],
    };
  }
}
