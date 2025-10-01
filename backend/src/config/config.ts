/**
 * Configuration management for AnomRadar Backend
 * Loads and validates environment variables
 */
export class Config {
  // Database
  public readonly dbHost: string;
  public readonly dbPort: number;
  public readonly dbName: string;
  public readonly dbUser: string;
  public readonly dbPassword: string;

  // YTJ API
  public readonly ytjApiKey: string;
  public readonly ytjApiUrl: string;

  // ZAP
  public readonly zapApiKey: string;
  public readonly zapApiUrl: string;

  // Nmap
  public readonly nmapPath: string;
  public readonly nmapOptions: string;

  // Scanner Settings
  public readonly simulationMode: boolean;
  public readonly scanTimeout: number;
  public readonly maxConcurrentScans: number;

  // Risk Scoring
  public readonly riskHighThreshold: number;
  public readonly riskMediumThreshold: number;
  public readonly riskLowThreshold: number;

  // Notifications
  public readonly telegramBotToken: string;
  public readonly telegramChatIds: string[];
  public readonly whatsappApiKey: string;
  public readonly whatsappEnabled: boolean;
  public readonly notificationsEnabled: boolean;

  // Logging
  public readonly logLevel: string;
  public readonly logFile: string;

  constructor() {
    // Database
    this.dbHost = process.env.DB_HOST || 'localhost';
    this.dbPort = parseInt(process.env.DB_PORT || '3306', 10);
    this.dbName = process.env.DB_NAME || 'anomradar';
    this.dbUser = process.env.DB_USER || 'anomradar';
    this.dbPassword = process.env.DB_PASSWORD || '';

    // YTJ API
    this.ytjApiKey = process.env.YTJ_API_KEY || '';
    this.ytjApiUrl = process.env.YTJ_API_URL || 'https://avoindata.prh.fi/bis/v1';

    // ZAP
    this.zapApiKey = process.env.ZAP_API_KEY || '';
    this.zapApiUrl = process.env.ZAP_API_URL || 'http://localhost:8080';

    // Nmap
    this.nmapPath = process.env.NMAP_PATH || '/usr/bin/nmap';
    this.nmapOptions = process.env.NMAP_OPTIONS || '-sV -sC';

    // Scanner Settings
    this.simulationMode = process.env.SIMULATION_MODE === 'true';
    this.scanTimeout = parseInt(process.env.SCAN_TIMEOUT || '300000', 10);
    this.maxConcurrentScans = parseInt(process.env.MAX_CONCURRENT_SCANS || '3', 10);

    // Risk Scoring
    this.riskHighThreshold = parseInt(process.env.RISK_HIGH_THRESHOLD || '70', 10);
    this.riskMediumThreshold = parseInt(process.env.RISK_MEDIUM_THRESHOLD || '40', 10);
    this.riskLowThreshold = parseInt(process.env.RISK_LOW_THRESHOLD || '20', 10);

    // Notifications
    this.telegramBotToken = process.env.TELEGRAM_BOT_TOKEN || '';
    this.telegramChatIds = (process.env.TELEGRAM_CHAT_IDS || '').split(',').filter(id => id.trim());
    this.whatsappApiKey = process.env.WHATSAPP_API_KEY || '';
    this.whatsappEnabled = process.env.WHATSAPP_ENABLED === 'true';
    this.notificationsEnabled = process.env.NOTIFICATIONS_ENABLED === 'true';

    // Logging
    this.logLevel = process.env.LOG_LEVEL || 'info';
    this.logFile = process.env.LOG_FILE || '/var/log/anomradar/backend.log';

    this.validate();
  }

  private validate(): void {
    if (!this.dbPassword) {
      console.warn('⚠️  Warning: DB_PASSWORD is not set');
    }

    if (this.simulationMode) {
      console.warn('⚠️  Warning: SIMULATION_MODE is enabled - scans will be simulated');
    }
  }
}
