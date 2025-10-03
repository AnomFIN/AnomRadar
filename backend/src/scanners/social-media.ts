import axios from 'axios';
import * as cheerio from 'cheerio';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';

export interface SocialMediaResult {
  findings: Finding[];
}

/**
 * Social Media Presence Scanner
 * Detects and analyzes company social media accounts
 */
export class SocialMediaScanner {
  private config: Config;

  // Common social media platforms
  private platforms = [
    { name: 'LinkedIn', urlPattern: 'linkedin.com/company/', icon: 'LinkedIn' },
    { name: 'Twitter', urlPattern: 'twitter.com/', icon: 'Twitter/X' },
    { name: 'Facebook', urlPattern: 'facebook.com/', icon: 'Facebook' },
    { name: 'Instagram', urlPattern: 'instagram.com/', icon: 'Instagram' },
    { name: 'YouTube', urlPattern: 'youtube.com/', icon: 'YouTube' },
    { name: 'TikTok', urlPattern: 'tiktok.com/', icon: 'TikTok' },
    { name: 'GitHub', urlPattern: 'github.com/', icon: 'GitHub' },
  ];

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<SocialMediaResult> {
    logger.info(`SocialMedia: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Scan website for social media links
      const socialLinks = await this.findSocialMediaLinks(domain);

      if (socialLinks.size === 0) {
        findings.push({
          type: 'social_no_presence',
          severity: 'low',
          title: 'No Social Media Presence Detected',
          description: 'No social media links found on the website',
          recommendation: 'Consider establishing social media presence for better brand visibility and customer engagement',
        });
      } else {
        findings.push({
          type: 'social_presence_found',
          severity: 'info',
          title: 'Social Media Presence Detected',
          description: `Found ${socialLinks.size} social media platform(s)`,
          evidence: {
            platforms: Array.from(socialLinks.keys()),
            links: Array.from(socialLinks.values()),
          },
        });

        // Check each platform
        for (const [platform, url] of socialLinks) {
          findings.push({
            type: 'social_platform_link',
            severity: 'info',
            title: `${platform} Profile Found`,
            description: `Found ${platform} profile`,
            evidence: { platform, url },
          });
        }

        // Check for missing major platforms
        const missingPlatforms = this.platforms
          .filter(p => !socialLinks.has(p.name))
          .map(p => p.name);

        if (missingPlatforms.length > 0) {
          findings.push({
            type: 'social_missing_platforms',
            severity: 'info',
            title: 'Potential Missing Social Media',
            description: `Not found on: ${missingPlatforms.join(', ')}`,
            recommendation: 'Consider expanding social media presence to these platforms',
            evidence: { missing: missingPlatforms },
          });
        }
      }

      // Check for HTTPS in social media links
      for (const [platform, url] of socialLinks) {
        if (url.startsWith('http://')) {
          findings.push({
            type: 'social_insecure_link',
            severity: 'low',
            title: 'Insecure Social Media Link',
            description: `${platform} link uses HTTP instead of HTTPS`,
            recommendation: 'Update to HTTPS for secure connections',
            evidence: { platform, url },
          });
        }
      }

      logger.info(`SocialMedia: Found ${findings.length} items for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`SocialMedia: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private async findSocialMediaLinks(domain: string): Promise<Map<string, string>> {
    const socialLinks = new Map<string, string>();

    try {
      // Fetch website content
      const response = await axios.get(`https://${domain}`, {
        timeout: 10000,
        headers: {
          'User-Agent': 'AnomRadar/1.0 (Security Scanner)',
        },
        maxRedirects: 5,
        validateStatus: (status) => status < 500,
      });

      if (response.status !== 200) {
        return socialLinks;
      }

      const $ = cheerio.load(response.data);

      // Extract all links
      const links = new Set<string>();
      $('a[href]').each((_, element) => {
        const href = $(element).attr('href');
        if (href) {
          links.add(href);
        }
      });

      // Check for social media patterns
      for (const link of links) {
        for (const platform of this.platforms) {
          if (link.includes(platform.urlPattern) && !socialLinks.has(platform.name)) {
            // Clean up and normalize URL
            let cleanUrl = link;
            if (cleanUrl.startsWith('//')) {
              cleanUrl = 'https:' + cleanUrl;
            } else if (cleanUrl.startsWith('/')) {
              cleanUrl = `https://${domain}${cleanUrl}`;
            }

            socialLinks.set(platform.name, cleanUrl);
          }
        }
      }

      // Also check meta tags for social media
      const metaTags = [
        'og:url',
        'twitter:url',
        'twitter:site',
        'article:publisher',
      ];

      for (const metaTag of metaTags) {
        const content = $(`meta[property="${metaTag}"]`).attr('content') ||
                       $(`meta[name="${metaTag}"]`).attr('content');
        
        if (content) {
          for (const platform of this.platforms) {
            if (content.includes(platform.urlPattern) && !socialLinks.has(platform.name)) {
              socialLinks.set(platform.name, content);
            }
          }
        }
      }

    } catch (error) {
      logger.warn(`SocialMedia: Failed to fetch ${domain}:`, error);
    }

    return socialLinks;
  }

  private simulateScan(domain: string): SocialMediaResult {
    logger.info('SocialMedia: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'social_simulation',
          severity: 'info',
          title: 'Social Media Simulation',
          description: `Simulated social media scan for ${domain}`,
        },
      ],
    };
  }
}
