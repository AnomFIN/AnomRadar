import { exec } from 'child_process';
import { promisify } from 'util';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

const execAsync = promisify(exec);

export interface DNSResult {
  findings: Finding[];
}

/**
 * DNS Scanner
 * Analyzes DNS records for security issues
 */
export class DNSScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<DNSResult> {
    logger.info(`DNS: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Check A records
      const aRecords = await this.lookupDNS(domain, 'A');
      if (!aRecords || aRecords.length === 0) {
        findings.push({
          type: 'dns_no_a_record',
          severity: 'medium',
          title: 'No A Record Found',
          description: `Domain ${domain} has no A records configured`,
          recommendation: 'Verify domain DNS configuration',
        });
      }

      // Check MX records
      const mxRecords = await this.lookupDNS(domain, 'MX');
      if (!mxRecords || mxRecords.length === 0) {
        findings.push({
          type: 'dns_no_mx_record',
          severity: 'low',
          title: 'No MX Record Found',
          description: `Domain ${domain} has no MX records configured`,
          recommendation: 'Configure MX records if email service is needed',
        });
      }

      // Check for DNSSEC
      const dnssecRecords = await this.lookupDNS(domain, 'DNSKEY');
      if (!dnssecRecords || dnssecRecords.length === 0) {
        findings.push({
          type: 'dns_no_dnssec',
          severity: 'medium',
          title: 'DNSSEC Not Configured',
          description: `Domain ${domain} does not have DNSSEC enabled`,
          recommendation: 'Consider enabling DNSSEC for enhanced security',
        });
      }

      return { findings };

    } catch (error) {
      logger.error(`DNS: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private async lookupDNS(domain: string, recordType: string): Promise<string[] | null> {
    try {
      const { stdout } = await execAsync(`dig +short ${domain} ${recordType}`);
      const records = stdout.trim().split('\n').filter(r => r.length > 0);
      return records.length > 0 ? records : null;
    } catch (error) {
      logger.error(`DNS: Lookup failed for ${domain} ${recordType}:`, error);
      return null;
    }
  }

  private simulateScan(domain: string): DNSResult {
    logger.info('DNS: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'dns_simulation',
          severity: 'info',
          title: 'DNS Simulation',
          description: `Simulated DNS scan for ${domain}`,
        },
      ],
    };
  }
}
