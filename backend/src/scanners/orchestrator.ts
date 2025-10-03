import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { YTJScanner } from './ytj';
import { DomainScanner } from './domain';
import { DNSScanner } from './dns';
import { SPFDMARCScanner } from './spf-dmarc';
import { ZAPScanner } from './zap';
import { NmapScanner } from './nmap';
import { ContactScraper } from './contact-scraper';
import { SSLScanner } from './ssl';
import { WHOISScanner } from './whois';
import { SocialMediaScanner } from './social-media';
import { TechStackScanner } from './tech-stack';
import { RiskScorer } from '../risk-scoring/risk-scorer';

export interface ScanResult {
  scanId: string;
  companyName: string;
  businessId?: string;
  domains: string[];
  findings: Finding[];
  riskScore: number;
  riskLevel: 'critical' | 'high' | 'medium' | 'low' | 'info';
  timestamp: Date;
}

export interface Finding {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  title: string;
  description: string;
  recommendation?: string;
  evidence?: any;
}

/**
 * Orchestrates all scanners and manages scan workflow
 */
export class ScannerOrchestrator {
  private config: Config;
  private ytjScanner: YTJScanner;
  private domainScanner: DomainScanner;
  private dnsScanner: DNSScanner;
  private spfDmarcScanner: SPFDMARCScanner;
  private zapScanner: ZAPScanner;
  private nmapScanner: NmapScanner;
  private contactScraper: ContactScraper;
  private sslScanner: SSLScanner;
  private whoisScanner: WHOISScanner;
  private socialMediaScanner: SocialMediaScanner;
  private techStackScanner: TechStackScanner;
  private riskScorer: RiskScorer;

  constructor(config: Config) {
    this.config = config;
    this.ytjScanner = new YTJScanner(config);
    this.domainScanner = new DomainScanner(config);
    this.dnsScanner = new DNSScanner(config);
    this.spfDmarcScanner = new SPFDMARCScanner(config);
    this.zapScanner = new ZAPScanner(config);
    this.nmapScanner = new NmapScanner(config);
    this.contactScraper = new ContactScraper(config);
    this.sslScanner = new SSLScanner(config);
    this.whoisScanner = new WHOISScanner(config);
    this.socialMediaScanner = new SocialMediaScanner(config);
    this.techStackScanner = new TechStackScanner(config);
    this.riskScorer = new RiskScorer(config);
  }

  async initialize(): Promise<void> {
    logger.info('Initializing scanner orchestrator...');
    logger.info(`Configuration: Simulation Mode = ${this.config.simulationMode}`);
    // Initialize scanners if needed
    logger.info('✓ Scanner orchestrator initialized');
  }

  async shutdown(): Promise<void> {
    logger.info('Shutting down scanner orchestrator...');
    // Cleanup if needed
  }

  /**
   * Run a complete scan for a company
   */
  async runScan(companyNameOrId: string): Promise<ScanResult> {
    const scanId = this.generateScanId();
    logger.info(`Starting scan ${scanId} for: ${companyNameOrId}`);

    const findings: Finding[] = [];
    let domains: string[] = [];
    let companyName = companyNameOrId;
    let businessId: string | undefined;

    try {
      // Step 1: YTJ Lookup
      logger.info(`[${scanId}] Step 1: YTJ lookup`);
      const ytjResult = await this.ytjScanner.scan(companyNameOrId);
      if (ytjResult) {
        companyName = ytjResult.name || companyName;
        businessId = ytjResult.businessId;
        domains = ytjResult.domains || [];
        findings.push(...ytjResult.findings);
      }

      // Step 2: Domain Discovery
      logger.info(`[${scanId}] Step 2: Domain discovery`);
      const additionalDomains = await this.domainScanner.scan(companyName);
      domains = [...new Set([...domains, ...additionalDomains])];

      // Step 3: DNS Analysis
      logger.info(`[${scanId}] Step 3: DNS analysis`);
      for (const domain of domains) {
        const dnsResult = await this.dnsScanner.scan(domain);
        findings.push(...dnsResult.findings);
      }

      // Step 4: SPF/DMARC Checks
      logger.info(`[${scanId}] Step 4: SPF/DMARC checks`);
      for (const domain of domains) {
        const emailSecResult = await this.spfDmarcScanner.scan(domain);
        findings.push(...emailSecResult.findings);
      }

      // Step 5: ZAP Passive Scan
      logger.info(`[${scanId}] Step 5: ZAP passive scan`);
      for (const domain of domains) {
        const zapResult = await this.zapScanner.scan(domain);
        findings.push(...zapResult.findings);
      }

      // Step 6: Nmap Scan
      logger.info(`[${scanId}] Step 6: Nmap scan`);
      for (const domain of domains) {
        const nmapResult = await this.nmapScanner.scan(domain);
        findings.push(...nmapResult.findings);
      }

      // Step 7: Contact Scraping
      logger.info(`[${scanId}] Step 7: Contact scraping`);
      for (const domain of domains) {
        const contactResult = await this.contactScraper.scan(domain);
        findings.push(...contactResult.findings);
      }

      // Step 8: SSL/TLS Certificate Check
      logger.info(`[${scanId}] Step 8: SSL/TLS certificate check`);
      for (const domain of domains) {
        const sslResult = await this.sslScanner.scan(domain);
        findings.push(...sslResult.findings);
      }

      // Step 9: WHOIS Lookup
      logger.info(`[${scanId}] Step 9: WHOIS lookup`);
      for (const domain of domains) {
        const whoisResult = await this.whoisScanner.scan(domain);
        findings.push(...whoisResult.findings);
      }

      // Step 10: Social Media Presence
      logger.info(`[${scanId}] Step 10: Social media presence check`);
      for (const domain of domains) {
        const socialResult = await this.socialMediaScanner.scan(domain);
        findings.push(...socialResult.findings);
      }

      // Step 11: Technology Stack Detection
      logger.info(`[${scanId}] Step 11: Technology stack detection`);
      for (const domain of domains) {
        const techResult = await this.techStackScanner.scan(domain);
        findings.push(...techResult.findings);
      }

      // Step 12: Risk Scoring
      logger.info(`[${scanId}] Step 12: Risk scoring`);
      const riskScore = this.riskScorer.calculateScore(findings);
      const riskLevel = this.riskScorer.getRiskLevel(riskScore);

      const result: ScanResult = {
        scanId,
        companyName,
        businessId,
        domains,
        findings,
        riskScore,
        riskLevel,
        timestamp: new Date(),
      };

      logger.info(`[${scanId}] ✓ Scan complete - Risk: ${riskLevel} (${riskScore})`);
      return result;

    } catch (error) {
      logger.error(`[${scanId}] Scan failed:`, error);
      throw error;
    }
  }

  private generateScanId(): string {
    return `scan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}
