import React, { useEffect, useRef } from 'react';
import PerfectScrollbar from 'perfect-scrollbar';
import { useTheme } from '@mui/material/styles';

interface CustomScrollbarProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

const CustomScrollbar: React.FC<CustomScrollbarProps> = ({ children, style, className, ...props }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const psRef = useRef<PerfectScrollbar | null>(null);
  const theme = useTheme();

  useEffect(() => {
    if (containerRef.current) {
      // Create custom CSS for theming
      const styleId = 'perfect-scrollbar-theme';
      let styleElement = document.getElementById(styleId) as HTMLStyleElement;
      
      if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = styleId;
        document.head.appendChild(styleElement);
      }

      const isDark = theme.palette.mode === 'dark';
      const trackBg = isDark ? 'rgba(255, 255, 255, 0.25)' : 'rgba(0, 0, 0, 0.15)';
      const thumbBg = isDark ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)';
      const thumbHoverBg = isDark ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.8)';

      styleElement.textContent = `
        .ps__rail-y {
          width: 6px !important;
          background-color: ${trackBg} !important;
          border-radius: 3px !important;
          right: 0px !important;
        }
        
        .ps__rail-x {
          height: 6px !important;
          background-color: ${trackBg} !important;
          border-radius: 3px !important;
          bottom: 0px !important;
        }
        
        .ps__thumb-y {
          width: 4px !important;
          background-color: ${thumbBg} !important;
          border-radius: 2px !important;
          margin: 1px !important;
          transition: background-color 0.2s ease !important;
        }
        
        .ps__thumb-x {
          height: 4px !important;
          background-color: ${thumbBg} !important;
          border-radius: 2px !important;
          margin: 1px !important;
          transition: background-color 0.2s ease !important;
        }
        
        .ps__thumb-y:hover {
          background-color: ${thumbHoverBg} !important;
        }
        
        .ps__thumb-x:hover {
          background-color: ${thumbHoverBg} !important;
        }
      `;

      // Initialize Perfect Scrollbar
      psRef.current = new PerfectScrollbar(containerRef.current, {
        wheelSpeed: 1,
        wheelPropagation: false,
        minScrollbarLength: 20,
      });
    }

    return () => {
      if (psRef.current) {
        psRef.current.destroy();
        psRef.current = null;
      }
    };
  }, [theme.palette.mode]);

  // Update scrollbar when content changes
  useEffect(() => {
    if (psRef.current) {
      psRef.current.update();
    }
  });

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
};

export default CustomScrollbar;