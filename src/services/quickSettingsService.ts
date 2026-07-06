import { Platform } from 'react-native';

// Android Quick Settings Tile for lock screen SOS access
// Users can add this tile to their notification shade for instant access even when device is locked

export interface QuickSettingsTile {
  id: string;
  label: string;
  icon: string;
  isActive: boolean;
}

class QuickSettingsService {
  private static instance: QuickSettingsService;
  private tiles: QuickSettingsTile[] = [];

  static getInstance(): QuickSettingsService {
    if (!QuickSettingsService.instance) {
      QuickSettingsService.instance = new QuickSettingsService();
    }
    return QuickSettingsService.instance;
  }

  async initialize(): Promise<void> {
    if (Platform.OS !== 'android') {
      return;
    }

    // Register the SOS tile
    await this.registerSOSTile();
  }

  private async registerSOSTile(): Promise<void> {
    if (Platform.OS !== 'android') {
      return;
    }

    // Android Quick Settings Tile registration
    // This requires native Android implementation, but we define the contract here
    const sosTile: QuickSettingsTile = {
      id: 'cocohub_sos',
      label: 'SOS Emergency',
      icon: 'sos_icon',
      isActive: true,
    };

    this.tiles.push(sosTile);

    // Note: Actual native implementation would go in android/app/src/main/java/.../SOSTileService.java
    // The tile will appear in Quick Settings panel, accessible even on lock screen
    console.log('[QuickSettings] SOS tile registered:', sosTile);
  }

  getTiles(): QuickSettingsTile[] {
    return this.tiles;
  }

  async handleTileClick(tileId: string): Promise<void> {
    if (tileId === 'cocohub_sos') {
      // Trigger SOS when tile is clicked from lock screen
      const emergencyService = (await import('./emergencyService')).default;
      await emergencyService.triggerSOS('Emergency SOS triggered from Quick Settings');
    }
  }
}

export default QuickSettingsService.getInstance();
