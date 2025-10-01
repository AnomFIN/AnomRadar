import { exec } from 'child_process';
import { promisify } from 'util';
import { Config } from '../config/config';
import { logger } from '../utils/logger';
import { Finding } from './orchestrator';
import { parseStringPromise } from 'xml2js';

const execAsync = promisify(exec);

export interface NmapResult {
  findings: Finding[];
}

/**
 * Nmap Scanner
 * Network port and service discovery
 */
export class NmapScanner {
  private config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async scan(domain: string): Promise<NmapResult> {
    logger.info(`Nmap: Scanning ${domain}`);

    if (this.config.simulationMode) {
      return this.simulateScan(domain);
    }

    const findings: Finding[] = [];

    try {
      // Run Nmap scan with XML output
      const command = `${this.config.nmapPath} ${this.config.nmapOptions} -oX - ${domain}`;
      logger.info(`Nmap: Running command: ${command}`);
      
      const { stdout } = await execAsync(command, {
        timeout: this.config.scanTimeout,
      });

      // Parse XML output
      const result = await parseStringPromise(stdout);
      
      if (result.nmaprun && result.nmaprun.host) {
        const hosts = Array.isArray(result.nmaprun.host) ? result.nmaprun.host : [result.nmaprun.host];
        
        hosts.forEach((host: any) => {
          if (host.ports && host.ports[0] && host.ports[0].port) {
            const ports = Array.isArray(host.ports[0].port) ? host.ports[0].port : [host.ports[0].port];
            
            ports.forEach((port: any) => {
              const portId = port.$.portid;
              const protocol = port.$.protocol;
              const state = port.state && port.state[0] ? port.state[0].$.state : 'unknown';
              const service = port.service && port.service[0] ? port.service[0].$.name : 'unknown';
              const version = port.service && port.service[0] ? port.service[0].$.version : '';

              if (state === 'open') {
                // Check for potentially risky services
                const riskyPorts = [21, 23, 445, 3389, 5900];
                const riskyServices = ['telnet', 'ftp', 'vnc', 'rdp'];
                
                let severity: 'critical' | 'high' | 'medium' | 'low' | 'info' = 'info';
                let recommendation = 'Review if this service needs to be publicly accessible';

                if (riskyPorts.includes(parseInt(portId, 10)) || riskyServices.some(s => service.includes(s))) {
                  severity = 'high';
                  recommendation = 'This service is potentially risky and should not be exposed to the internet';
                }

                findings.push({
                  type: 'nmap_open_port',
                  severity,
                  title: `Open Port: ${portId}/${protocol}`,
                  description: `Service: ${service} ${version}`.trim(),
                  recommendation,
                  evidence: {
                    port: portId,
                    protocol,
                    service,
                    version,
                    state,
                  },
                });
              }
            });
          }

          // Check for script results
          if (host.hostscript && host.hostscript[0] && host.hostscript[0].script) {
            const scripts = Array.isArray(host.hostscript[0].script) ? host.hostscript[0].script : [host.hostscript[0].script];
            
            scripts.forEach((script: any) => {
              findings.push({
                type: 'nmap_script',
                severity: 'info',
                title: `Script: ${script.$.id}`,
                description: script.$.output || 'No output',
                evidence: {
                  scriptId: script.$.id,
                  output: script.$.output,
                },
              });
            });
          }
        });
      }

      logger.info(`Nmap: Found ${findings.length} items for ${domain}`);
      return { findings };

    } catch (error) {
      logger.error(`Nmap: Scan failed for ${domain}:`, error);
      return { findings };
    }
  }

  private simulateScan(domain: string): NmapResult {
    logger.info('Nmap: SIMULATION MODE - Returning mock findings');
    return {
      findings: [
        {
          type: 'nmap_simulation',
          severity: 'info',
          title: 'Nmap Simulation',
          description: `Simulated Nmap scan for ${domain}`,
        },
      ],
    };
  }
}
