import { exec } from 'child_process';
import { promisify } from 'util';
import https from 'https';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

const execAsync = promisify(exec);

export interface SSLResult {
  findings: Finding[];
}

/**
 * SSL/TLS Certificate Scanner
 * Checks SSL certificate validity, expiration, and security issues
 */
export class SSLScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<SSLResult> {
    logger.info(`SSL: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Get SSL certificate information
      const certInfo = await this.getCertificateInfo(domain);

      if (!certInfo) {
        findings.push({
          type: 'ssl_no_certificate',
          severity: 'high',
          title: 'No SSL Certificate',
          description: `Domain ${domain} does not have a valid SSL certificate`,
          recommendation: 'Install an SSL certificate from a trusted Certificate Authority',
          evidence: { domain },
        });
        return { findings };
      }

      // Check certificate expiration
      const daysUntilExpiry = Math.floor(
        (new Date(certInfo.valid_to).getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      );

      if (daysUntilExpiry < 0) {
        findings.push({
          type: 'ssl_expired',
          severity: 'critical',
          title: 'SSL Certificate Expired',
          description: `Certificate expired ${Math.abs(daysUntilExpiry)} days ago`,
          recommendation: 'Renew the SSL certificate immediately',
          evidence: {
            valid_to: certInfo.valid_to,
            expired_days: Math.abs(daysUntilExpiry),
          },
        });
      } else if (daysUntilExpiry < 30) {
        findings.push({
          type: 'ssl_expiring_soon',
          severity: 'high',
          title: 'SSL Certificate Expiring Soon',
          description: `Certificate expires in ${daysUntilExpiry} days`,
          recommendation: 'Renew the SSL certificate as soon as possible',
          evidence: {
            valid_to: certInfo.valid_to,
            days_remaining: daysUntilExpiry,
          },
        });
      } else if (daysUntilExpiry < 90) {
        findings.push({
          type: 'ssl_expiring',
          severity: 'medium',
          title: 'SSL Certificate Expiring',
          description: `Certificate expires in ${daysUntilExpiry} days`,
          recommendation: 'Plan to renew the certificate soon',
          evidence: {
            valid_to: certInfo.valid_to,
            days_remaining: daysUntilExpiry,
          },
        });
      }

      // Check for self-signed certificate
      if (certInfo.issuer === certInfo.subject) {
        findings.push({
          type: 'ssl_self_signed',
          severity: 'high',
          title: 'Self-Signed SSL Certificate',
          description: 'Certificate is self-signed and not trusted by browsers',
          recommendation: 'Use a certificate from a trusted Certificate Authority',
          evidence: {
            issuer: certInfo.issuer,
            subject: certInfo.subject,
          },
        });
      }

      // Check certificate algorithm
      if (certInfo.algorithm && (certInfo.algorithm.includes('SHA1') || certInfo.algorithm.includes('MD5'))) {
        findings.push({
          type: 'ssl_weak_algorithm',
          severity: 'high',
          title: 'Weak SSL Algorithm',
          description: `Certificate uses weak algorithm: ${certInfo.algorithm}`,
          recommendation: 'Use SHA-256 or stronger algorithm',
          evidence: { algorithm: certInfo.algorithm },
        });
      }

      // Check for wildcard certificate issues
      if (certInfo.subject_alt_names && certInfo.subject_alt_names.some((name: string) => name.startsWith('*.'))) {
        findings.push({
          type: 'ssl_wildcard',
          severity: 'info',
          title: 'Wildcard SSL Certificate',
          description: 'Certificate is a wildcard certificate',
          recommendation: 'Ensure wildcard certificates are necessary and properly secured',
          evidence: { alt_names: certInfo.subject_alt_names },
        });
      }

      // Check SSL Labs grade using openssl
      try {
        const sslLabsInfo = await this.checkSSLConfiguration(domain);
        if (sslLabsInfo.weakProtocols.length > 0) {
          findings.push({
            type: 'ssl_weak_protocols',
            severity: 'high',
            title: 'Weak SSL/TLS Protocols Enabled',
            description: `Weak protocols detected: ${sslLabsInfo.weakProtocols.join(', ')}`,
            recommendation: 'Disable SSLv2, SSLv3, TLS 1.0, and TLS 1.1. Use TLS 1.2 or TLS 1.3 only',
            evidence: { protocols: sslLabsInfo.weakProtocols },
          });
        }

        if (sslLabsInfo.weakCiphers.length > 0) {
          findings.push({
            type: 'ssl_weak_ciphers',
            severity: 'medium',
            title: 'Weak SSL Ciphers Enabled',
            description: `Weak ciphers detected: ${sslLabsInfo.weakCiphers.join(', ')}`,
            recommendation: 'Disable weak ciphers and use strong cipher suites',
            evidence: { ciphers: sslLabsInfo.weakCiphers },
          });
        }
      } catch (err) {
        // SSL Labs check failed, continue
      }

      logger.info(`SSL: Found ${findings.length} issues for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`SSL: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private async getCertificateInfo(domain: string): Promise<any> {
    return new Promise((resolve) => {
      const options = {
        host: domain,
        port: 443,
        method: 'GET',
        rejectUnauthorized: false, // Allow self-signed for analysis
      };

      const req = https.request(options, (res) => {
        const cert = (res.socket as any).getPeerCertificate();
        if (cert && Object.keys(cert).length > 0) {
          resolve({
            subject: cert.subject?.CN || 'Unknown',
            issuer: cert.issuer?.CN || 'Unknown',
            valid_from: cert.valid_from,
            valid_to: cert.valid_to,
            algorithm: cert.signatureAlgorithm,
            subject_alt_names: cert.subjectaltname?.split(', ').map((s: string) => s.replace('DNS:', '')),
          });
        } else {
          resolve(null);
        }
      });

      req.on('error', () => {
        resolve(null); // No certificate available
      });

      req.end();
    });
  }

  private async checkSSLConfiguration(domain: string): Promise<{ weakProtocols: string[]; weakCiphers: string[] }> {
    const weakProtocols: string[] = [];
    const weakCiphers: string[] = [];

    try {
      // Check for weak protocols
      const protocols = ['ssl2', 'ssl3', 'tls1', 'tls1_1'];
      for (const protocol of protocols) {
        try {
          const { stdout } = await execAsync(
            `echo | openssl s_client -connect ${domain}:443 -${protocol} 2>&1 | grep "Protocol" | head -1`,
            { timeout: 5000 }
          );
          if (stdout && !stdout.includes('error') && !stdout.includes('wrong version')) {
            weakProtocols.push(protocol.toUpperCase().replace('_', '.'));
          }
        } catch (e) {
          // Protocol not supported (good)
        }
      }

      // Check for weak ciphers
      const weakCipherPatterns = ['DES', 'RC4', 'MD5', 'EXPORT', 'NULL', 'anon'];
      try {
        const { stdout } = await execAsync(
          `echo | openssl s_client -connect ${domain}:443 -cipher 'ALL' 2>&1 | grep "Cipher" | head -1`,
          { timeout: 5000 }
        );
        
        weakCipherPatterns.forEach(pattern => {
          if (stdout.includes(pattern)) {
            weakCiphers.push(pattern);
          }
        });
      } catch (e) {
        // Cipher check failed
      }

    } catch (error) {
      // SSL configuration check failed
    }

    return { weakProtocols, weakCiphers };
  }

  private simulateScan(domain: string): SSLResult {
    logger.info('SSL: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'ssl_simulation',
          severity: 'info',
          title: 'SSL Simulation',
          description: `Simulated SSL scan for ${domain}`,
        },
      ],
    };
  }
}
