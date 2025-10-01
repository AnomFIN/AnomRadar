import axios from 'axios';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

export interface ZAPResult {
  findings: Finding[];
}

/**
 * OWASP ZAP Passive Scanner
 * Performs passive security scanning using OWASP ZAP
 * NOTE: Only passive scanning - no active attacks
 */
export class ZAPScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<ZAPResult> {
    logger.info(`ZAP: Passive scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      if (!this.config.zapApiKey) {
        logger.warn('ZAP: API key not configured, skipping');
        return { findings };
      }

      const targetUrl = `https://${domain}`;

      // Spider the site (passive)
      await this.zapSpider(targetUrl);

      // Wait for passive scan to complete
      await this.waitForPassiveScan();

      // Get alerts
      const alerts = await this.getAlerts(targetUrl);

      // Convert ZAP alerts to findings
      alerts.forEach((alert: any) => {
        const severity = this.mapZAPSeverity(alert.risk);
        findings.push({
          type: `zap_${alert.pluginId}`,
          severity,
          title: alert.name,
          description: alert.description,
          recommendation: alert.solution,
          evidence: {
            url: alert.url,
            param: alert.param,
            attack: alert.attack,
            evidence: alert.evidence,
          },
        });
      });

      logger.info(`ZAP: Found ${findings.length} issues for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`ZAP: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private async zapSpider(targetUrl: string): Promise<void> {
    try {
      const response = await axios.get(`${this.config.zapApiUrl}/JSON/spider/action/scan/`, {
        params: {
          apikey: this.config.zapApiKey,
          url: targetUrl,
          maxChildren: 10, // Limit depth
        },
        timeout: this.config.scanTimeout,
      });

      const scanId = response.data.scan;
      logger.info(`ZAP: Spider started with ID ${scanId}`);

      // Wait for spider to complete
      let progress = 0;
      while (progress < 100) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        const statusResponse = await axios.get(`${this.config.zapApiUrl}/JSON/spider/view/status/`, {
          params: {
            apikey: this.config.zapApiKey,
            scanId,
          },
        });
        progress = parseInt(statusResponse.data.status, 10);
      }

      logger.info('ZAP: Spider complete');
    } catch (error) {
      logger.error('ZAP: Spider failed:', error);
      throw error;
    }
  }

  private async waitForPassiveScan(): Promise<void> {
    try {
      let recordsToScan = 1;
      while (recordsToScan > 0) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const response = await axios.get(`${this.config.zapApiUrl}/JSON/pscan/view/recordsToScan/`, {
          params: {
            apikey: this.config.zapApiKey,
          },
        });
        recordsToScan = parseInt(response.data.recordsToScan, 10);
      }
      logger.info('ZAP: Passive scan complete');
    } catch (error) {
      logger.error('ZAP: Passive scan wait failed:', error);
    }
  }

  private async getAlerts(targetUrl: string): Promise<any[]> {
    try {
      const response = await axios.get(`${this.config.zapApiUrl}/JSON/core/view/alerts/`, {
        params: {
          apikey: this.config.zapApiKey,
          baseurl: targetUrl,
        },
      });
      return response.data.alerts || [];
    } catch (error) {
      logger.error('ZAP: Failed to get alerts:', error);
      return [];
    }
  }

  private mapZAPSeverity(risk: string): 'critical' | 'high' | 'medium' | 'low' | 'info' {
    switch (risk.toLowerCase()) {
      case 'high':
        return 'high';
      case 'medium':
        return 'medium';
      case 'low':
        return 'low';
      default:
        return 'info';
    }
  }

  private simulateScan(domain: string): ZAPResult {
    logger.info('ZAP: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'zap_simulation',
          severity: 'info',
          title: 'ZAP Simulation',
          description: `Simulated ZAP passive scan for ${domain}`,
        },
      ],
    };
  }
}
