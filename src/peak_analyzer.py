"""
Peak-Based Chromatograph Analysis
Detects and measures peaks (A0, A2, F, etc.) for clinical-grade similarity
"""

import cv2
import numpy as np
from PIL import Image
from scipy.signal import find_peaks, peak_widths
from typing import Dict, List, Tuple
import io
import re
import pytesseract

class PeakAnalyzer:
    """Analyzes chromatograph peaks for medical similarity comparison"""
    
    def __init__(self):
        """Initialize peak analyzer"""
        pass
    
    def extract_chromatograph_region(self, image: Image.Image) -> np.ndarray:
        """
        Extract the actual chromatograph graph region from the image
        
        Args:
            image: PIL Image of chromatograph
            
        Returns:
            numpy array of the graph region
        """
        # Convert to grayscale
        img_array = np.array(image.convert('L'))
        
        # Find the graph region (usually bottom 60% has the actual graph)
        height = img_array.shape[0]
        
        # Take bottom 60% where graph typically is
        graph_region = img_array[int(height*0.4):, :]
        
        return graph_region
    
    def detect_baseline(self, signal: np.ndarray) -> float:
        """
        Detect baseline of chromatograph signal
        
        Args:
            signal: 1D signal array
            
        Returns:
            Baseline value
        """
        # Use bottom 10th percentile as baseline
        baseline = np.percentile(signal, 10)
        return baseline
    
    def extract_signal_profile(self, graph_region: np.ndarray, sigma: float = 2.0) -> np.ndarray:
        """
        Extract 1D signal profile from graph region
        
        Args:
            graph_region: 2D numpy array of graph
            
        Returns:
            1D signal profile
        """
        # Invert if needed (dark peaks on light background)
        mean_val = np.mean(graph_region)
        if mean_val > 127:  # Light background
            graph_region = 255 - graph_region
        
        # Take vertical average to get signal
        signal = np.mean(graph_region, axis=0)
        
        # Smooth signal
        from scipy.ndimage import gaussian_filter1d
        signal_smooth = gaussian_filter1d(signal, sigma=sigma)
        
        return signal_smooth
    
    def detect_peaks_from_signal(self, signal: np.ndarray,
                                 prominence: float = 0.15,
                                 height: float = 0.1,
                                 distance: int = 20,
                                 width: int = 5) -> Dict:
        """
        Detect peaks from 1D signal profile
        
        Args:
            signal: 1D signal array
            
        Returns:
            Dictionary with peak information
        """
        # Normalize signal
        signal = signal - np.min(signal)
        signal = signal / (np.max(signal) + 1e-6)
        
        # Detect peaks
        # Parameters tuned for chromatograph peaks (stricter to avoid noise)
        peaks, properties = find_peaks(
            signal,
            prominence=prominence,
            distance=distance,
            width=width,
            height=height
        )
        
        # Get peak heights
        peak_heights = signal[peaks]
        
        # Get peak widths
        widths = peak_widths(signal, peaks, rel_height=0.5)[0]
        
        # Calculate peak areas (approximate)
        peak_areas = peak_heights * widths
        
        # Sort by position (left to right)
        sort_idx = np.argsort(peaks)
        peaks = peaks[sort_idx]
        peak_heights = peak_heights[sort_idx]
        widths = widths[sort_idx]
        peak_areas = peak_areas[sort_idx]
        
        return {
            'num_peaks': len(peaks),
            'positions': peaks.tolist(),
            'heights': peak_heights.tolist(),
            'widths': widths.tolist(),
            'areas': peak_areas.tolist(),
            'signal_length': len(signal)
        }
    
    def analyze_image(self, image: Image.Image) -> Dict:
        """
        Complete analysis of chromatograph image
        
        Args:
            image: PIL Image
            
        Returns:
            Dictionary with all features
        """
        # Extract graph region
        graph_region = self.extract_chromatograph_region(image)
        
        # Extract signal profile
        signal = self.extract_signal_profile(graph_region)
        
        # Detect peaks (strict first pass)
        peak_info = self.detect_peaks_from_signal(signal)
        peak_info['detection_mode'] = 'strict'
        
        # If too few peaks detected, retry with increasingly sensitive settings
        if peak_info['num_peaks'] < 3:
            peak_info = self.detect_peaks_from_signal(
                signal,
                prominence=0.05,
                height=0.05,
                distance=15,
                width=3
            )
            peak_info['detection_mode'] = 'sensitive'
        
        if peak_info['num_peaks'] < 3:
            peak_info = self.detect_peaks_from_signal(
                signal,
                prominence=0.02,
                height=0.02,
                distance=8,
                width=2
            )
            peak_info['detection_mode'] = 'very_sensitive'
        
        if peak_info['num_peaks'] < 3:
            # Recompute signal with lighter smoothing and ultra-sensitive params
            alt_signal = self.extract_signal_profile(graph_region, sigma=1.0)
            peak_info = self.detect_peaks_from_signal(
                alt_signal,
                prominence=0.01,
                height=0.01,
                distance=5,
                width=1
            )
            peak_info['detection_mode'] = 'ultra_sensitive'
        
        # Final fallback: widen smoothing and reduce prominence further
        if peak_info['num_peaks'] < 3:
            alt_signal = self.extract_signal_profile(graph_region, sigma=3.0)
            peak_info = self.detect_peaks_from_signal(
                alt_signal,
                prominence=0.005,
                height=0.005,
                distance=4,
                width=1
            )
            peak_info['detection_mode'] = 'ultra_sensitive_wide'
        
        # Calculate additional features
        features = {
            **peak_info,
            'total_signal_intensity': float(np.sum(signal)),
            'mean_intensity': float(np.mean(signal)),
            'std_intensity': float(np.std(signal)),
        }
        
        # OCR to extract reported concentrations (F%, A2%)
        a2_val = None
        f_val = None
        try:
            w, h = image.size
            regions = [
                image,  # full
                image.crop((0, 0, w, int(h*0.7))),                # top 70%
                image.crop((0, int(h*0.3), w, int(h*0.8))),       # middle band
                image.crop((int(w*0.05), int(h*0.45), int(w*0.95), int(h*0.75))) # band around concentration text above graph
            ]
            texts = []
            for reg in regions:
                gray = np.array(reg.convert('L'))
                gray = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 35, 11
                )
                kernel = np.ones((1, 1), np.uint8)
                gray = cv2.dilate(gray, kernel, iterations=1)
                txt = pytesseract.image_to_string(
                    Image.fromarray(gray),
                    config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.%AacntrsoF '
                )
                texts.append(txt)
            full_text = "\n".join(texts)
            a2_match = re.search(r"A2\\s*Concentration[^0-9]*([0-9]+\\.?[0-9]*)\\s*%?", full_text, re.IGNORECASE)
            if not a2_match:
                a2_match = re.search(r"A2[^\\d]*([0-9]+\\.?[0-9]*)\\s*%?", full_text, re.IGNORECASE)
            f_match = re.search(r"F\\s*Concentration[^0-9]*([0-9]+\\.?[0-9]*)\\s*%?", full_text, re.IGNORECASE)
            if not f_match:
                f_match = re.search(r"\\bF[^\\d]*([0-9]+\\.?[0-9]*)\\s*%?", full_text, re.IGNORECASE)
            if a2_match:
                a2_val = float(a2_match.group(1))
            if f_match:
                f_val = float(f_match.group(1))
        except Exception:
            pass
        features['a2_concentration'] = a2_val
        features['f_concentration'] = f_val
        
        # Normalize positions to 0-1 range
        if features['num_peaks'] > 0:
            norm_positions = [p / features['signal_length'] for p in features['positions']]
            features['normalized_positions'] = norm_positions
        else:
            features['normalized_positions'] = []
        
        return features
    
    def is_clinically_similar(self, features1: Dict, features2: Dict, 
                             max_concentration_ratio: float = 2.5,
                             max_peak_count_diff: int = 3) -> tuple[bool, str]:
        """
        Hard filter: Determine if two chromatographs are similar enough to compare.
        
        Clinical exclusion criteria:
        - Any peak concentration differs by >2.5x (e.g., 3% vs 8% = NO!)
        - Peak count differs by >3 (e.g., 4 peaks vs 13 peaks = NO!)
        
        Returns:
            (is_similar: bool, reason: str)
        """
        # Check 1: Peak count difference
        num_diff = abs(features1['num_peaks'] - features2['num_peaks'])
        if num_diff > max_peak_count_diff:
            return False, f"Peak count too different ({features1['num_peaks']} vs {features2['num_peaks']})"
        
        # Check 2: Peak concentration (height) ratios
        if features1['num_peaks'] > 0 and features2['num_peaks'] > 0:
            heights1 = np.array(features1['heights'])
            heights2 = np.array(features2['heights'])
            
            # Compare each peak pair
            max_len = max(len(heights1), len(heights2))
            if len(heights1) < max_len:
                heights1 = np.pad(heights1, (0, max_len - len(heights1)))
            if len(heights2) < max_len:
                heights2 = np.pad(heights2, (0, max_len - len(heights2)))
            
            for i, (h1, h2) in enumerate(zip(heights1, heights2)):
                # Skip if both are very small (noise or missing peaks)
                if h1 < 0.05 and h2 < 0.05:
                    continue
                
                # Skip if one is missing (padded zero) but other is small
                if (h1 < 0.01 and h2 < 0.15) or (h2 < 0.01 and h1 < 0.15):
                    continue  # Don't penalize for small missing peaks
                
                # Calculate ratio (avoid division by zero)
                if min(h1, h2) < 0.01:  # One peak is essentially zero
                    # If the other peak is also small, skip it
                    if max(h1, h2) < 0.2:  # <20% is a minor peak
                        continue
                    # If one is zero and other is significant, that's a real difference
                    ratio = 100.0  # Treat as very different
                else:
                    ratio = max(h1, h2) / min(h1, h2)
                
                # Hard cutoff: >max_concentration_ratio difference = TOO DIFFERENT
                # Examples at current threshold (4.0x):
                # - INCLUDED: 3% vs 4.2% = 1.4x ✅
                # - INCLUDED: 3% vs 10% = 3.3x ✅
                # - EXCLUDED: 3% vs 13% = 4.3x ❌
                # - EXCLUDED: 3% vs 27% = 9x ❌❌
                if ratio > max_concentration_ratio:
                    return False, f"Peak #{i+1} concentration too different ({h1:.1%} vs {h2:.1%}, ratio={ratio:.1f}x)"
        
        return True, "Clinically similar"
    
    def calculate_peak_similarity(self, features1: Dict, features2: Dict) -> float:
        """
        Calculate similarity based on peak features (BALANCED clinical criteria)
        
        Balanced approach:
        - Peak heights (concentrations): 35%
        - Retention time (positions): 35%
        - Peak count: 15%
        - Overall intensity: 15%
        
        Note: Hard filter already excluded extreme differences
        
        Args:
            features1: Features from image 1
            features2: Features from image 2
            
        Returns:
            Similarity score (0-1), details dict
        """
        scores = []
        
        # 1. Number of peaks similarity (15%)
        num_diff = abs(features1['num_peaks'] - features2['num_peaks'])
        if num_diff == 0:
            num_peaks_sim = 1.0
        elif num_diff == 1:
            num_peaks_sim = 0.8
        elif num_diff == 2:
            num_peaks_sim = 0.6
        else:
            num_peaks_sim = 0.4
        scores.append(('num_peaks', num_peaks_sim, 0.15))
        
        # 2. Peak height (concentration) similarity (35%)
        if features1['num_peaks'] > 0 and features2['num_peaks'] > 0:
            heights1 = np.array(features1['heights'])
            heights2 = np.array(features2['heights'])
            
            # Match peaks by position
            max_len = max(len(heights1), len(heights2))
            if len(heights1) < max_len:
                heights1 = np.pad(heights1, (0, max_len - len(heights1)))
            if len(heights2) < max_len:
                heights2 = np.pad(heights2, (0, max_len - len(heights2)))
            
            # Calculate ratios for each peak pair
            height_sims = []
            for h1, h2 in zip(heights1, heights2):
                if h1 < 0.01 and h2 < 0.01:
                    height_sims.append(1.0)
                    continue
                
                # Calculate ratio (larger/smaller)
                ratio = max(h1, h2) / (min(h1, h2) + 1e-6)
                
                # Exponential decay for differences
                if ratio < 1.5:  # Similar (e.g., 3.4% vs 4.2%)
                    sim = 1.0
                elif ratio < 2.0:
                    sim = 0.85
                elif ratio < 3.0:
                    sim = 0.6
                else:  # >3x difference (but <4x since filter would exclude >=4x)
                    sim = 0.3
                
                height_sims.append(sim)
            
            height_sim = np.mean(height_sims)
        else:
            height_sim = 0.0
        scores.append(('heights', height_sim, 0.35))
        
        # 3. Retention time (position) similarity (35%)
        if features1['num_peaks'] > 0 and features2['num_peaks'] > 0:
            pos1 = np.array(features1['normalized_positions'])
            pos2 = np.array(features2['normalized_positions'])
            
            max_len = max(len(pos1), len(pos2))
            if len(pos1) < max_len:
                pos1 = np.pad(pos1, (0, max_len - len(pos1)), constant_values=999)
            if len(pos2) < max_len:
                pos2 = np.pad(pos2, (0, max_len - len(pos2)), constant_values=999)
            
            # Calculate position differences
            pos_sims = []
            for p1, p2 in zip(pos1, pos2):
                if p1 == 999 or p2 == 999:
                    pos_sims.append(0.5)
                    continue
                
                # Approximate time difference
                approx_time_diff = abs(p1 - p2) * 10.0  # minutes
                
                # Apply retention time threshold
                if approx_time_diff < 0.1:
                    sim = 1.0
                elif approx_time_diff < 0.2:
                    sim = 0.95
                elif approx_time_diff < 0.4:  # User's threshold
                    sim = 0.85
                elif approx_time_diff < 0.6:
                    sim = 0.6
                else:
                    sim = 0.3
                
                pos_sims.append(sim)
            
            pos_sim = np.mean(pos_sims)
        else:
            pos_sim = 0.0
        scores.append(('retention_time', pos_sim, 0.35))
        
        # 4. Overall intensity pattern (15%)
        intensity_diff = abs(features1['mean_intensity'] - features2['mean_intensity'])
        intensity_sim = np.exp(-intensity_diff * 2)
        scores.append(('intensity', intensity_sim, 0.15))
        
        # Weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        
        # Debug info
        details = {name: f"{score:.3f}" for name, score, _ in scores}
        details['total'] = f"{total_score:.3f}"
        
        return total_score, details


# Singleton instance
_peak_analyzer = None

def get_peak_analyzer() -> PeakAnalyzer:
    """Get or create singleton peak analyzer instance"""
    global _peak_analyzer
    if _peak_analyzer is None:
        _peak_analyzer = PeakAnalyzer()
    return _peak_analyzer

