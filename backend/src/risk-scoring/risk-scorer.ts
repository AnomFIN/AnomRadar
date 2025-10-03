import { Config } from '../config/config';
import { Finding } from '../scanners/orchestrator';
import { logger } from '../utils/logger';

/**
 * Risk Scorer
 * Calculates overall risk score based on findings
 */
export class RiskScorer {
  private config: Config;

  // Severity weights
  private readonly weights = {
    critical: 25,
    high: 15,
    medium: 8,
    low: 3,
    info: 0,
  };

  constructor(config: Config) {
    this.config = config;
  }

  /**
   * Calculate risk score from findings
   * Score is 0-100, where 100 is highest risk
   */
  calculateScore(findings: Finding[]): number {
    if (!findings || findings.length === 0) {
      return 0;
    }

    let totalScore = 0;
    const severityCounts = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0,
    };

    // Count findings by severity and calculate base score
    findings.forEach(finding => {
      const severity = finding.severity;
      severityCounts[severity]++;
      totalScore += this.weights[severity];
    });

    // Apply diminishing returns for multiple findings of same type
    // (More findings increase risk but not linearly)
    const adjustedScore = Math.min(100, totalScore * 0.8 + Math.sqrt(findings.length) * 2);

    logger.info('Risk Scoring:', {
      totalFindings: findings.length,
      severityCounts,
      rawScore: totalScore,
      adjustedScore: Math.round(adjustedScore),
    });

    return Math.round(adjustedScore);
  }

  /**
   * Get risk level based on score
   */
  getRiskLevel(score: number): 'critical' | 'high' | 'medium' | 'low' | 'info' {
    if (score >= this.config.riskHighThreshold) {
      return 'high';
    } else if (score >= this.config.riskMediumThreshold) {
      return 'medium';
    } else if (score >= this.config.riskLowThreshold) {
      return 'low';
    } else {
      return 'info';
    }
  }

  /**
   * Get risk level description
   */
  getRiskDescription(riskLevel: string): string {
    const descriptions = {
      critical: 'Critical security issues detected - immediate action required',
      high: 'High risk - address these issues as soon as possible',
      medium: 'Medium risk - should be addressed in the near term',
      low: 'Low risk - minor issues that can be addressed over time',
      info: 'Informational - no significant risks detected',
    };

    return descriptions[riskLevel as keyof typeof descriptions] || descriptions.info;
  }

  /**
   * Get prioritized findings (highest severity first)
   */
  prioritizeFindings(findings: Finding[]): Finding[] {
    const severityOrder = ['critical', 'high', 'medium', 'low', 'info'];
    
    return [...findings].sort((a, b) => {
      return severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity);
    });
  }

  /**
   * Get summary statistics
   */
  getSummary(findings: Finding[]) {
    const summary = {
      total: findings.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0,
    };

    findings.forEach(finding => {
      summary[finding.severity]++;
    });

    return summary;
  }
}
