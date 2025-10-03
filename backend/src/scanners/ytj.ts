import axios from 'axios';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

export interface YTJResult {
  name: string;
  businessId: string;
  domains: string[];
  findings: Finding[];
}

/**
 * YTJ (Finnish Business Registry) Scanner
 * Looks up company information from the Finnish Business Information System
 */
export class YTJScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(companyNameOrId: string): Promise<YTJResult | null> {
    logger.info(`YTJ: Scanning for ${companyNameOrId}`);

    if (this.config.simulationMode) {
      return this.simulateScan(companyNameOrId);
    }

    try {
      if (!this.config.ytjApiKey) {
        logger.warn('YTJ: API key not configured, skipping');
        return null;
      }

      // Search for company by name or business ID
      const searchUrl = `${this.config.ytjApiUrl}/companies?name=${encodeURIComponent(companyNameOrId)}`;
      const response = await axios.get(searchUrl, {
        headers: {
          'Accept': 'application/json',
        },
        timeout: this.config.scanTimeout,
      });

      const findings: Finding[] = [];
      const domains: string[] = [];

      if (response.data && response.data.results && response.data.results.length > 0) {
        const company = response.data.results[0];
        
        // Extract domains from contact information
        if (company.contactDetails) {
          const websites = company.contactDetails.filter((c: any) => c.type === 'Website');
          websites.forEach((site: any) => {
            try {
              const url = new URL(site.value);
              domains.push(url.hostname);
            } catch (e) {
              // Invalid URL, skip
            }
          });
        }

        // Check company status
        if (company.companyForm && company.companyForm.toLowerCase().includes('konkurssi')) {
          findings.push({
            type: 'ytj_company_status',
            severity: 'high',
            title: 'Company in Bankruptcy',
            description: 'The company appears to be in bankruptcy or liquidation',
            recommendation: 'Verify company status before engaging',
          });
        }

        return {
          name: company.name,
          businessId: company.businessId,
          domains,
          findings,
        };
      }

      logger.warn(`YTJ: No results found for ${companyNameOrId}`);
      return null;

    } catch (error) {
      logger.error('YTJ: Scan failed:', error);
      return null;
    }
  }

  private simulateScan(companyNameOrId: string): YTJResult {
    logger.info('YTJ: SIMULATION MODE - Returning mock data');
    return {
      name: companyNameOrId,
      businessId: '1234567-8',
      domains: ['example.com', 'example.fi'],
      findings: [
        {
          type: 'ytj_simulation',
          severity: 'info',
          title: 'Simulation Mode',
          description: 'This is simulated YTJ data',
        },
      ],
    };
  }
}
