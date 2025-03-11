export interface ScanResult {
  id: string;
  patientName: string;
  patientId: string;
  imageType: string;
  uploadTime: string;
  processedImage: string | null;
  numDetections: number;
  confidences: number[];
  status: 'completed' | 'failed';
  error?: string;
}

export interface StoredScan extends ScanResult {
  originalImage: string;
}

export function saveScanToHistory(scan: StoredScan) {
  try {
    // Get existing history
    const history = JSON.parse(localStorage.getItem('scanHistory') || '[]') as StoredScan[];
    
    // Add new scan to front of array
    history.unshift(scan);
    
    // Keep only last 50 scans
    const trimmedHistory = history.slice(0, 50);
    
    // Save back to localStorage
    localStorage.setItem('scanHistory', JSON.stringify(trimmedHistory));
    
    return true;
  } catch (error) {
    console.error('Error saving scan to history:', error);
    return false;
  }
}

export function getScanHistory(): StoredScan[] {
  try {
    return JSON.parse(localStorage.getItem('scanHistory') || '[]');
  } catch (error) {
    console.error('Error reading scan history:', error);
    return [];
  }
}

export function clearScanHistory(): void {
  localStorage.removeItem('scanHistory');
}

export function deleteScan(id: string): boolean {
  try {
    const history = getScanHistory();
    const filteredHistory = history.filter(scan => scan.id !== id);
    localStorage.setItem('scanHistory', JSON.stringify(filteredHistory));
    return true;
  } catch (error) {
    console.error('Error deleting scan:', error);
    return false;
  }
}
