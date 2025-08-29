import { useEffect, useRef, useState } from 'react';

/**
 * Hook for managing focus trap in modals and dialogs
 */
export function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    const handleEscapeKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        // Let parent component handle escape
        event.stopPropagation();
      }
    };

    document.addEventListener('keydown', handleTabKey);
    document.addEventListener('keydown', handleEscapeKey);
    
    // Focus first element when trap becomes active
    firstElement?.focus();

    return () => {
      document.removeEventListener('keydown', handleTabKey);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [isActive]);

  return containerRef;
}

/**
 * Hook for announcing dynamic content changes to screen readers
 */
export function useAriaLiveRegion() {
  const regionRef = useRef<HTMLDivElement | null>(null);

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (!regionRef.current) {
      // Create region if it doesn't exist
      const region = document.createElement('div');
      region.setAttribute('aria-live', priority);
      region.setAttribute('aria-atomic', 'true');
      region.style.position = 'absolute';
      region.style.left = '-10000px';
      region.style.width = '1px';
      region.style.height = '1px';
      region.style.overflow = 'hidden';
      document.body.appendChild(region);
      regionRef.current = region;
    }

    // Update the message
    regionRef.current.textContent = message;
    
    // Clear after announcement
    setTimeout(() => {
      if (regionRef.current) {
        regionRef.current.textContent = '';
      }
    }, 1000);
  };

  useEffect(() => {
    return () => {
      if (regionRef.current && regionRef.current.parentNode) {
        regionRef.current.parentNode.removeChild(regionRef.current);
      }
    };
  }, []);

  return announce;
}

/**
 * Hook for keyboard navigation in lists
 */
export function useKeyboardNavigation(
  items: any[],
  onSelect: (index: number) => void,
  isActive: boolean = true
) {
  const selectedIndexRef = useRef(-1);
  const containerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          selectedIndexRef.current = Math.min(selectedIndexRef.current + 1, items.length - 1);
          focusItem(selectedIndexRef.current);
          break;
        
        case 'ArrowUp':
          event.preventDefault();
          selectedIndexRef.current = Math.max(selectedIndexRef.current - 1, 0);
          focusItem(selectedIndexRef.current);
          break;
        
        case 'Home':
          event.preventDefault();
          selectedIndexRef.current = 0;
          focusItem(selectedIndexRef.current);
          break;
        
        case 'End':
          event.preventDefault();
          selectedIndexRef.current = items.length - 1;
          focusItem(selectedIndexRef.current);
          break;
        
        case 'Enter':
        case ' ':
          event.preventDefault();
          if (selectedIndexRef.current >= 0) {
            onSelect(selectedIndexRef.current);
          }
          break;
      }
    };

    const focusItem = (index: number) => {
      const items = containerRef.current?.querySelectorAll('[role="option"], [role="menuitem"], [role="listitem"]');
      const item = items?.[index] as HTMLElement;
      item?.focus();
    };

    containerRef.current.addEventListener('keydown', handleKeyDown);

    return () => {
      containerRef.current?.removeEventListener('keydown', handleKeyDown);
    };
  }, [items.length, onSelect, isActive]);

  return containerRef;
}

/**
 * Helper function to generate unique IDs for form elements
 */
export function useId(prefix: string = 'id'): string {
  const idRef = useRef<string | undefined>(undefined);
  
  if (!idRef.current) {
    idRef.current = `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
  }
  
  return idRef.current;
}

/**
 * Hook for managing reduced motion preferences
 */
export function useReducedMotion(): boolean {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return prefersReducedMotion;
}

/**
 * Color contrast utilities
 */
export const colorUtils = {
  /**
   * Calculate contrast ratio between two colors
   */
  getContrastRatio(foreground: string, background: string): number {
    const getLuminance = (color: string): number => {
      // Simplified luminance calculation
      // In a real implementation, you'd convert hex/rgb to linear RGB
      const hex = color.replace('#', '');
      const r = parseInt(hex.substr(0, 2), 16) / 255;
      const g = parseInt(hex.substr(2, 2), 16) / 255;
      const b = parseInt(hex.substr(4, 2), 16) / 255;
      
      const toLinear = (c: number) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      
      return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);
    };

    const lum1 = getLuminance(foreground);
    const lum2 = getLuminance(background);
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    
    return (brightest + 0.05) / (darkest + 0.05);
  },

  /**
   * Check if color combination meets WCAG AA standards
   */
  meetsWCAGAA(foreground: string, background: string): boolean {
    return this.getContrastRatio(foreground, background) >= 4.5;
  },

  /**
   * Check if color combination meets WCAG AAA standards
   */
  meetsWCAGAAA(foreground: string, background: string): boolean {
    return this.getContrastRatio(foreground, background) >= 7;
  }
};