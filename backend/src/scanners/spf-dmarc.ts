import { exec } from 'child_process';
import { promisify } from 'util';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

const execAsync = promisify(exec);

export interface SPFDMARCResult {
  findings: Finding[];
}

/**
 * SPF/DMARC Scanner
 * Checks email security policies (SPF, DMARC, DKIM)
 */
export class SPFDMARCScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<SPFDMARCResult> {
    logger.info(`SPF/DMARC: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Check SPF record
      const spfRecord = await this.lookupTXT(domain, 'v=spf1');
      if (!spfRecord) {
        findings.push({
          type: 'email_no_spf',
          severity: 'high',
          title: 'No SPF Record',
          description: `Domain ${domain} does not have an SPF record configured`,
          recommendation: 'Configure SPF record to prevent email spoofing',
          evidence: { domain },
        });
      } else {
        // Check for weak SPF configurations
        if (spfRecord.includes('+all') || spfRecord.includes('?all')) {
          findings.push({
            type: 'email_weak_spf',
            severity: 'high',
            title: 'Weak SPF Configuration',
            description: `SPF record allows unrestricted email sending (+all or ?all)`,
            recommendation: 'Use -all or ~all to prevent email spoofing',
            evidence: { spfRecord },
          });
        }
      }

      // Check DMARC record
      const dmarcRecord = await this.lookupTXT(`_dmarc.${domain}`, 'v=DMARC1');
      if (!dmarcRecord) {
        findings.push({
          type: 'email_no_dmarc',
          severity: 'high',
          title: 'No DMARC Record',
          description: `Domain ${domain} does not have a DMARC record configured`,
          recommendation: 'Configure DMARC policy to protect against email spoofing',
          evidence: { domain },
        });
      } else {
        // Check DMARC policy
        if (dmarcRecord.includes('p=none')) {
          findings.push({
            type: 'email_weak_dmarc',
            severity: 'medium',
            title: 'Weak DMARC Policy',
            description: `DMARC policy is set to 'none' (monitoring only)`,
            recommendation: 'Consider strengthening policy to quarantine or reject',
            evidence: { dmarcRecord },
          });
        }
      }

      // Check DKIM (basic check for common selectors)
      const dkimSelectors = ['default', 'mail', 'google', 'k1', 'selector1', 'selector2'];
      let hasDKIM = false;
      for (const selector of dkimSelectors) {
        const dkimRecord = await this.lookupTXT(`${selector}._domainkey.${domain}`, 'v=DKIM1');
        if (dkimRecord) {
          hasDKIM = true;
          break;
        }
      }

      if (!hasDKIM) {
        findings.push({
          type: 'email_no_dkim',
          severity: 'medium',
          title: 'DKIM Not Detected',
          description: `Could not detect DKIM configuration for common selectors`,
          recommendation: 'Configure DKIM signing for email authentication',
          evidence: { domain, selectorsChecked: dkimSelectors },
        });
      }

      return { findings };

    } catch (error) {
      logger.error(`SPF/DMARC: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private async lookupTXT(domain: string, filterPrefix: string): Promise<string | null> {
    try {
      const { stdout } = await execAsync(`dig +short ${domain} TXT`);
      const records = stdout.trim().split('\n')
        .map(r => r.replace(/"/g, ''))
        .filter(r => r.startsWith(filterPrefix));
      return records.length > 0 ? records[0] : null;
    } catch (error) {
      return null;
    }
  }

  private simulateScan(domain: string): SPFDMARCResult {
    logger.info('SPF/DMARC: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'email_simulation',
          severity: 'info',
          title: 'Email Security Simulation',
          description: `Simulated SPF/DMARC scan for ${domain}`,
        },
      ],
    };
  }
}
